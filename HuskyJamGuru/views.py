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

            issues = json.loads(
                    get_gitlab(self.request).get("http://185.22.60.142:8889/api/v3/issues").content.decode("utf-8")
            )

            # print(issues)

            for project in projects:
                print(project["name"])
                for issue in issues:
                    if issue["project_id"] == project["id"]:
                        print(issue)

            # context['issues'] = issues
        return context


class Login(TemplateView):
    template_name = "HuskyJamGuru/login.html"