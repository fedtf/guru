import json

from django.views.generic import TemplateView

from Project.gitlab import get_gitlab


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
