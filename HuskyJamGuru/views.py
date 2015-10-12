from django.conf import settings
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, FormView, View
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.contrib.auth import get_user_model, login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render

from braces import views as braces_views

from Project.gitlab import load_new_and_update_existing_projects_from_gitlab
from .models import Project, UserToProjectAccess, IssueTimeAssessment, GitLabIssue,\
    GitLabMilestone


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


def synchronise_with_gitlab(request):
    load_new_and_update_existing_projects_from_gitlab(request)
    return HttpResponse()


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
        return render(reverse_lazy('project-list'))

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
