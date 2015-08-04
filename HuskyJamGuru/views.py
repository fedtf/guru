from django.views.generic import TemplateView


class Dashboard(TemplateView):
    template_name = "HuskyJamGuru/dashboard.html"


class Login(TemplateView):
    template_name = "HuskyJamGuru/login.html"


class Logout(TemplateView):
    template_name = "HuskyJamGuru/login.html"
