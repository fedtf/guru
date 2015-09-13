import json

from django.views.generic import TemplateView, ListView, DetailView, CreateView
from django.core.urlresolvers import reverse_lazy

from Project.gitlab import get_gitlab, load_new_and_update_existing_projects_from_gitlab
from .models import Project, UserToProjectAccess, IssueTimeAssessment, GitLabIssue


class Dashboard(TemplateView):
    template_name = "HuskyJamGuru/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super(Dashboard, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated():
            projects = json.loads(
                get_gitlab(self.request).get("http://185.22.60.142:8889/api/v3/projects").content.decode("utf-8")
            )

            issues_closed = json.loads(
                get_gitlab(self.request).get(
                    "http://185.22.60.142:8889/api/v3/issues?state=closed"
                ).content.decode("utf-8")
            )

            issues_opened = json.loads(
                get_gitlab(self.request).get(
                    "http://185.22.60.142:8889/api/v3/issues?state=opened"
                ).content.decode("utf-8")
            )

            milestones = json.loads(
                get_gitlab(self.request).get(
                    "http://185.22.60.142:8889/api/v3/projects/7/milestones"
                ).content.decode("utf-8")
            )

            context['issues_opened'] = issues_opened
            context['issues_closed'] = issues_closed
            context['projects'] = projects
            context['milestones'] = milestones

        return context


class Login(TemplateView):
    template_name = "HuskyJamGuru/login.html"


class ProjectListView(ListView):
    template_name = "HuskyJamGuru/project_list.html"
    model = Project
    context_object_name = 'project_list'

    def get_queryset(self):
        return UserToProjectAccess.get_projects_queryset_user_has_access_to(self.request.user, 'developer')

    def get_context_data(self, **kwargs):
        load_new_and_update_existing_projects_from_gitlab(self.request)
        context = super(self.__class__, self).get_context_data(**kwargs)
        return context


class ProjectDetailView(DetailView):
    template_name = "HuskyJamGuru/project_detail.html"
    model = Project
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        return context


class IssueTimeAssessmentCreate(CreateView):
    template_name = "HuskyJamGuru/issue_time_assessment_create.html"
    model = IssueTimeAssessment
    fields = ['minutes', 'gitlab_issue', 'user']
    success_url = reverse_lazy("HuskyJamGuru:project-list")

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        return context

    # def form_valid(self, form):
    #     form_valid = super(self.__class__, self).form_valid(form)
    #     self.object.user = self.request.user
    #     self.object.gitlab_issue = GitLabIssue.objects.get(pk=self.kwargs['issue_pk'])
    #     self.object.save()
    #     return form_valid

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

