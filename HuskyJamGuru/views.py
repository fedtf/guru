import uuid
import json
import datetime
import logging

from django.conf import settings
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, FormView, View
from django.views.generic.detail import SingleObjectMixin
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect, HttpResponseBadRequest
from django.contrib.auth import get_user_model, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist

from braces import views as braces_views
from celery.result import AsyncResult

from Project.gitlab import load_new_and_update_existing_projects_from_gitlab
from .models import Project, UserToProjectAccess, IssueTimeAssessment, GitLabIssue,\
    GitLabMilestone, GitlabProject, PersonalNotification, PersonalDayWorkPlan
from .forms import PersonalPlanForm, ProjectFormSet, ProjectForm
from .tasks import send_notifications, change_user_notification_state, pull_new_issue_from_gitlab


logger = logging.getLogger(__name__)


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


class ResourceManagementView(braces_views.LoginRequiredMixin, braces_views.SuperuserRequiredMixin, TemplateView):
    template_name = 'HuskyJamGuru/resource_management.html'

    def get_context_data(self, **kwargs):
        context = super(ResourceManagementView, self).get_context_data(**kwargs)
        dates = ()
        last_date = datetime.datetime.today().date() - datetime.timedelta(days=7)
        for i in range(21):
            dates += (last_date, )
            last_date += datetime.timedelta(days=1)
        context['today'] = datetime.datetime.today().date()
        context['dates'] = dates
        context['projects'] = Project.objects.filter(status='in-development').all()
        context['projects_per_user_amount'] = {}
        accesses = UserToProjectAccess.objects.filter().all()
        for access in accesses:
            if access.user not in context['projects_per_user_amount']:
                context['projects_per_user_amount'][access.user] = 0
            context['projects_per_user_amount'][access.user] += 1
        return context


class PersonalPlanUpdateView(braces_views.LoginRequiredMixin, FormView):
    template_name = 'HuskyJamGuru/personal_plan.html'
    form_class = PersonalPlanForm

    def get_initial(self):
        initial = super(PersonalPlanUpdateView, self).get_initial()
        work_plans = PersonalDayWorkPlan.get_work_plan(
            self.request.user,
            datetime.datetime.today().date() + datetime.timedelta(days=1),
            datetime.datetime.today() + datetime.timedelta(days=7 + 1)
        )
        for work_plan in work_plans:
            initial[
                'day_%i' % (work_plan.date - datetime.datetime.today().date() - datetime.timedelta(days=1)).days
            ] = work_plan.work_hours
        return initial

    def form_valid(self, form):
        for i in range(7):
            date = datetime.datetime.today() + datetime.timedelta(days=i + 1)
            current_work_plan = PersonalDayWorkPlan.get_work_plan(self.request.user, date, date)
            if not form.cleaned_data['day_%s' % i] == '':
                if len(current_work_plan) == 0 or \
                        current_work_plan[0].work_hours != int(form.cleaned_data['day_%s' % i]):
                    PersonalDayWorkPlan(
                        user=self.request.user, date=date, work_hours=int(form.cleaned_data['day_%s' % i])
                    ).save()
        return super(PersonalPlanUpdateView, self).form_valid(form)

    def get_success_url(self):
        message = 'Plan successfully updated!'
        messages.add_message(self.request, messages.SUCCESS, message)
        return reverse_lazy('HuskyJamGuru:personal-plan')


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
                            braces_views.JSONResponseMixin,
                            View):
    raise_exception = True

    def get_ajax(self, request):
        task_id = request.GET.get('task_id')

        result = AsyncResult(task_id)

        task = {
            'status': result.status,
            'id': result.id,
        }
        return self.render_json_response(task)


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
    form_class = ProjectForm
    template_name = 'HuskyJamGuru/project_update.html'

    def test_func(self, user):
        return (user.is_superuser or
                'manager' in user.gitlabauthorisation.to_project_access_types(self.get_object()))

    def get_form(self, form_class=None):
        form = super(ProjectUpdateView, self).get_form(form_class)
        form.fields['deadline_date'].required = False
        form.fields['issues_types'].required = False
        return form

    def get_context_data(self, **kwargs):
        context = super(ProjectUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ProjectFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = ProjectFormSet(instance=self.object)
        return context

    def get_success_url(self):
        message = 'Project successfully updated!'
        messages.add_message(self.request, messages.SUCCESS, message)
        return reverse_lazy('HuskyJamGuru:project-update', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        self.object = form.save(commit=True)
        formset.instance = self.object
        if formset.is_valid():
            formset.save(commit=True)
        return HttpResponseRedirect(self.get_success_url())


class ConfigureMilestoneView(braces_views.LoginRequiredMixin,
                             braces_views.SuperuserRequiredMixin,
                             SingleObjectMixin,
                             View):
    # Base view for changing privileged milestone properties.
    raise_exception = True
    model = GitLabMilestone

    def configure_milestone(self, milestone):
        raise NotImplementedError('You should provide configure_milestone method.')

    def get(self, request, *args, **kwargs):
        return redirect(reverse_lazy('HuskyJamGuru:project-list'))

    def post(self, request, *args, **kwargs):
        milestone = self.get_object()
        try:
            self.configure_milestone(milestone)
        except Exception as e:
            return HttpResponseBadRequest(e)

        if request.is_ajax():
            return HttpResponse()

        return redirect(reverse_lazy('HuskyJamGuru:project-detail',
                                     kwargs={'pk': milestone.gitlab_project.project.pk}))


class SortMilestoneView(ConfigureMilestoneView):
    def configure_milestone(self, milestone):
        direction = self.request.POST.get('direction')

        milestone_priority = milestone.priority

        if direction == 'up':
            swap_milestone = milestone.gitlab_project.gitlab_milestones \
                .filter(priority__lt=milestone_priority).last()
        elif direction == 'down':
            swap_milestone = milestone.gitlab_project.gitlab_milestones \
                .filter(priority__gt=milestone_priority).first()
        else:
            raise Exception("Invalid direction.")

        if swap_milestone is not None:
            milestone.priority = swap_milestone.priority
            swap_milestone.priority = milestone_priority

            milestone.save()
            swap_milestone.save()
        else:
            raise Exception("Can't move first milestone higher, or last - lower.")


class RollMilestoneView(ConfigureMilestoneView):
    def configure_milestone(self, milestone):
        milestone.rolled_up = not milestone.rolled_up
        milestone.save()


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


class GitlabWebhookView(braces_views.CsrfExemptMixin, View):
    def post(self, request, *args, **kwargs):
        if request.body:
            webhook_info = json.loads(request.body.decode('utf-8'))
            send_notifications.delay(webhook_info)
            if webhook_info['object_kind'] == 'issue' and webhook_info['object_attributes']['action'] != 'close':
                pull_new_issue_from_gitlab.delay(webhook_info)
        return HttpResponse()


class ChangeUserNotificationStateView(braces_views.LoginRequiredMixin,
                                      braces_views.UserPassesTestMixin,
                                      View):
    raise_exception = True

    def test_func(self, user):
        try:
            self.notification = user.notification
        except ObjectDoesNotExist:
            return False

        return str(user.pk) == self.kwargs.get('user_pk')

    def post(self, request, *args, **kwargs):
        new_state = request.POST.get('new_state')
        if new_state:
            task = change_user_notification_state.delay(new_state, self.notification)
            return HttpResponse(task.id)
        else:
            return HttpResponseBadRequest()


class UserProfileView(braces_views.LoginRequiredMixin,
                      braces_views.UserPassesTestMixin,
                      UpdateView):
    model = PersonalNotification
    fields = ['telegram_notification_events', 'email_notification_events']
    template_name = 'HuskyJamGuru/user_profile.html'
    success_url = reverse_lazy("HuskyJamGuru:project-list")
    raise_exception = True

    def test_func(self, user):
        return str(user.pk) == self.kwargs.get('pk')

    def get_object(self):
        try:
            notification = self.request.user.notification
        except ObjectDoesNotExist:
            notification = PersonalNotification.objects.create(user=self.request.user, telegram_id=uuid.uuid4().hex)
        return notification

    def get_form(self, form_class):
        form = super(UserProfileView, self).get_form(form_class)
        form.events = [event[1] for event in self.get_object().EVENTS]
        form.fields['telegram_notification_events'].label = 'Telegram'
        form.fields['email_notification_events'].label = 'E-mail'
        return form
