import json

from django.views.generic import TemplateView, ListView, DetailView

from Project.gitlab import get_gitlab, load_new_and_update_existing_projects_from_gitlab
from .models import Project, UserToProjectAccess


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
