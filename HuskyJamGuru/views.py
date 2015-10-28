import logging
import uuid
import json

from django.conf import settings
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, FormView, View
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse, HttpResponseNotFound
from django.contrib.auth import get_user_model, login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt

from braces import views as braces_views
from celery.result import AsyncResult
from rest_framework.reverse import reverse as full_path_reverse_lazy

from Project.gitlab import load_new_and_update_existing_projects_from_gitlab, fix_milestones_id
from .models import Project, UserToProjectAccess, IssueTimeAssessment, GitLabIssue,\
    GitLabMilestone, GitlabProject, TelegramUser
from .telegram_bot import telegram_bot


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def milestones_fix(request):
    fix_milestones_id(request)
    return redirect(reverse_lazy('HuskyJamGuru:project-list'))


class Login(TemplateView):
    template_name = "HuskyJamGuru/login.html"


class LoginAsGuruUserView(FormView):
    form_class = AuthenticationForm
    template_name = "admin/login.html"

    def form_valid(self, form):
        login(self.request, form.get_user())
        return redirect(settings.LOGIN_REDIRECT_URL)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class ProjectListView(ListView):
    template_name = "HuskyJamGuru/project_list.html"
    model = Project
    context_object_name = 'project_list'

    def get_queryset(self):
        return UserToProjectAccess.get_projects_queryset_user_has_access_to(self.request.user, 'developer')

    def get_context_data(self, **kwargs):
        context = super(ProjectListView, self).get_context_data(**kwargs)
        return context


class UpdateItemFromGitlabView(braces_views.LoginRequiredMixin,
                               braces_views.AjaxResponseMixin,
                               View):
    def get_ajax(self, request, *args, **kwargs):
        item_name = request.GET.get('item_name')
        item_pk = request.GET.get('item_pk')

        item = False

        if item_name == 'project':
            item = Project.objects.get(pk=item_pk)
        elif item_name == 'gitlab_project':
            item = GitlabProject.objects.get(pk=item_pk)
        elif item_name == 'milestone':
            item = GitLabMilestone.objects.get(pk=item_pk)
        elif item_name == 'issue':
            item = GitLabIssue.objects.get(pk=item_pk)

        if not item:
            return HttpResponseNotFound()

        task = item.update_from_gitlab.delay()

        return HttpResponse(task.id)


def synchronise_with_gitlab(request):
    task = load_new_and_update_existing_projects_from_gitlab.delay()
    return HttpResponse(task.id)


class CheckIfTaskIsDoneView(braces_views.LoginRequiredMixin,
                            braces_views.AjaxResponseMixin,
                            View):
    raise_exception = True

    def get_ajax(self, request):
        task_id = request.GET.get('task_id')

        result = AsyncResult(task_id)

        if result.successful():
            status = 'done'
        else:
            status = 'in work'
        return HttpResponse(status)


class ProjectDetailView(DetailView):
    template_name = "HuskyJamGuru/project_detail.html"
    model = Project
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super(ProjectDetailView, self).get_context_data(**kwargs)
        context['user_to_project_accesses'] = self.request.user.gitlabauthorisation.to_project_access_types(self.object)

        show_unassigned_column = False
        type_list = [type_tuple[0] for type_tuple in self.object.issues_types_tuple]
        for issue in self.object.issues.all():
            if issue.current_type.type not in type_list:
                show_unassigned_column = True
                break
        context['show_unassigned_column'] = show_unassigned_column

        show_unassigned_milestone = False
        for issue in self.object.issues.all():
            if issue.gitlab_milestone is None:
                show_unassigned_milestone = True
                break
        context['show_unassigned_milestone'] = show_unassigned_milestone
        return context


class ProjectUpdateView(braces_views.LoginRequiredMixin,
                        braces_views.UserPassesTestMixin,
                        UpdateView):
    model = Project
    fields = ['finish_date_assessment', 'issues_types']
    template_name = 'HuskyJamGuru/project_update.html'

    def test_func(self, user):
        return (user.is_superuser or
                'manager' in user.gitlabauthorisation.to_project_access_types(self.get_object()))

    def get_form(self, form_class):
        form = super(ProjectUpdateView, self).get_form(form_class)
        form.fields['finish_date_assessment'].help_text = 'e.g. 2015-10-8'
        form.fields['finish_date_assessment'].required = False
        form.fields['issues_types'].required = False
        return form


class SortMilestonesView(braces_views.LoginRequiredMixin,
                         braces_views.SuperuserRequiredMixin,
                         View):
    raise_exception = True

    def get(self, request):
        return redirect(reverse_lazy('project-list'))

    def post(self, request, *args, **kwargs):
        milestone_id = request.POST.get('milestone_id')
        direction = request.POST.get('direction')

        milestone = GitLabMilestone.objects.get(pk=milestone_id)
        milestone_priority = milestone.priority

        if direction == 'up':
            next_milestone = milestone.gitlab_project.gitlab_milestones\
                .filter(priority__lt=milestone_priority).last()
            if next_milestone is not None:
                milestone.priority = next_milestone.priority
                next_milestone.priority = milestone_priority

                milestone.save()
                next_milestone.save()
        elif direction == 'down':
            prev_milestone = milestone.gitlab_project.gitlab_milestones\
                .filter(priority__gt=milestone_priority).first()
            if prev_milestone is not None:
                milestone.priority = prev_milestone.priority
                prev_milestone.priority = milestone_priority

                milestone.save()
                prev_milestone.save()

        if request.is_ajax():
            return HttpResponse()

        return redirect(reverse_lazy('HuskyJamGuru:project-detail',
                                     kwargs={'pk': milestone.gitlab_project.project.pk}))


class ProjectReportView(DetailView):
    template_name = "HuskyJamGuru/project_report.html"
    model = Project
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super(ProjectReportView, self).get_context_data(**kwargs)
        context['report_list'] = self.object.report_list
        return context


class IssueTimeAssessmentCreate(CreateView):
    template_name = "HuskyJamGuru/issue_time_assessment_create.html"
    model = IssueTimeAssessment
    fields = ['minutes', 'gitlab_issue', 'user']
    success_url = reverse_lazy("HuskyJamGuru:project-list")

    def get_context_data(self, **kwargs):
        context = super(IssueTimeAssessmentCreate, self).get_context_data(**kwargs)
        return context

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        form.data._mutable = True
        form.data['gitlab_issue'] = GitLabIssue.objects.get(pk=self.kwargs['issue_pk']).pk
        form.data['user'] = self.request.user.pk
        form.data._mutable = False
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_initial(self):
        initials = {
            "gitlab_issue": GitLabIssue.objects.get(pk=self.kwargs['issue_pk']),
            'user': self.request.user
        }
        return initials

    def get_form(self, form_class=None):
        form = super(self.__class__, self).get_form(form_class)
        form.fields['gitlab_issue'].widget.attrs['disabled'] = True
        form.fields['user'].widget.attrs['disabled'] = True
        return form


class WorkReportListView(braces_views.LoginRequiredMixin,
                         braces_views.SuperuserRequiredMixin,
                         braces_views.PrefetchRelatedMixin,
                         braces_views.SelectRelatedMixin,
                         ListView):
    model = get_user_model()
    template_name = 'HuskyJamGuru/work_report_list.html'
    prefetch_related = ['issues_time_spent_records__gitlab_issue__gitlab_milestone',
                        'to_project_accesses']
    select_related = ['gitlabauthorisation__name']

    def get_queryset(self):
        queryset = super(WorkReportListView, self).get_queryset()
        for user in queryset:
            user.time_spent_records = user.issues_time_spent_records.all()[:6]
        return queryset


class PersonalTimeReportView(braces_views.LoginRequiredMixin,
                             braces_views.SuperuserRequiredMixin,
                             braces_views.PrefetchRelatedMixin,
                             DetailView):
    model = get_user_model()
    template_name = 'HuskyJamGuru/personal_time_report.html'
    context_object_name = 'report_user'
    prefetch_related = ['issues_time_spent_records__gitlab_issue__gitlab_milestone']


@csrf_exempt
def gitlab_webhook(request):
    with open('debug-log.txt', 'a') as f:
        print('got webhook from gitlab {}, {}'.format(request.POST, request.body), file=f)

    if request.body:
        webhook_info = json.loads(request.body.decode('utf-8'))
        project = GitlabProject.objects.get(project_id=webhook_info['project_id']).project

        message_text = ("Hi there, {user_name}! There is a new {event_type} from {event_emitter} "
                        "in the project {project_name}. C'mon checkout!")

        for user in set(access.user for access in project.user_project_accesses.all()):
            try:
                telegram_user = user.telegram_user
            except ObjectDoesNotExist:
                continue
            if telegram_user.notification_enabled and webhook_info['object_kind'] in telegram_user.notification_events:
                telegram_bot.sendMessage(chat_id=telegram_user.telegram_id,
                                         text=message_text.format(user_name=user.gitlabauthorisation.name,
                                                                  event_type=webhook_info['object_kind'],
                                                                  event_emitter=webhook_info['user_name'],
                                                                  project_name=project.name))
    return HttpResponse()


@csrf_exempt
def telegram_webhook(request):
    logger.info('got request webhook; {}'.format(request.body))
    return HttpResponse()


def set_webhook(request):
    full_path_for_webhook = full_path_reverse_lazy('HuskyJamGuru:telegram-webhook', request=request)
    response = telegram_bot.setWebhook(full_path_for_webhook)
    logger.info('set request webhook; response: {}'.format(response))
    return HttpResponse(full_path_reverse_lazy('HuskyJamGuru:telegram-webhook', request=request))


class UserProfileView(braces_views.LoginRequiredMixin,
                      braces_views.UserPassesTestMixin,
                      UpdateView):
    model = TelegramUser
    fields = ['notification_events']
    template_name = 'HuskyJamGuru/user_profile.html'
    success_url = reverse_lazy("HuskyJamGuru:project-list")
    raise_exception = True

    def test_func(self, user):
        return str(user.pk) == self.kwargs.get('pk')

    def get_object(self):
        try:
            telegram_user = self.request.user.telegram_user
        except ObjectDoesNotExist:
            telegram_user = TelegramUser.objects.create(user=self.request.user, telegram_id=uuid.uuid4().hex)
        return telegram_user

    def get_form(self, form_class):
        form = super(UserProfileView, self).get_form(form_class)
        form['notification_events'].label = 'Choose kinds of events that you whant to be notified about:'
        return form

    def post(self, request, *args, **kwargs):
        if request.POST.get('notification_enabled') == 'False':
            request.user.telegram_user.notification_enabled = False
            request.user.telegram_user.save()
            return redirect(self.success_url)
        else:
            return super(UserProfileView, self).post(request, *args, **kwargs)
