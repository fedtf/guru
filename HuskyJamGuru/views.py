from django.views.generic import TemplateView, ListView, DetailView, CreateView, View
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render

from braces import views as braces_views

from Project.gitlab import load_new_and_update_existing_projects_from_gitlab
from .models import Project, UserToProjectAccess, IssueTimeAssessment, GitLabIssue,\
    GitLabMilestone


class AdminRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(AdminRequiredMixin, cls).as_view(**initkwargs)
        return user_passes_test(lambda u: u.is_superuser)(view)


class Login(TemplateView):
    template_name = "HuskyJamGuru/login.html"


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
        context['user_to_project_access'] = UserToProjectAccess.objects.get(user=self.request.user,
                                                                            project=self.object)
        return context


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


class WorkReportListView(AdminRequiredMixin, ListView):
    template_name = 'HuskyJamGuru/work_report_list.html'
    prefetch_string = '{}__{}__{}'.format('issues_time_spent_records',
                                          'gitlab_issue',
                                          'gitlab_milestone')
    queryset = get_user_model().objects.all().prefetch_related(prefetch_string)\
                                             .select_related('gitlabauthorisation__name')
