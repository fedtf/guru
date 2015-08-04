from django.views.generic import TemplateView
from requests_oauthlib import OAuth2Session
from django.contrib.auth import authenticate, login as django_login
from django.contrib.auth.models import User
from .models import GitlabAuthorisation
import json
from django.core.exceptions import ObjectDoesNotExist

from django.http import HttpResponseRedirect, HttpResponse


class Dashboard(TemplateView):
    template_name = "HuskyJamGuru/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super(Dashboard, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated():
            gitlab = get_gitlab(self.request)
            r = gitlab.get("http://185.22.60.142:8889/api/v3/issues?state=opened")
            issues = json.loads(r.content.decode("utf-8"))
            context['issues'] = issues
        return context


def get_gitlab(request = None):
    client_id = r'9bc472164fc76c3dda596f01205cba2bb63a47d4e57d59fd5dd01762b3042721'
    redirect_uri = 'http://127.0.0.1:8000/gitlab_auth_redirect'
    if request is None:
        gitlab = OAuth2Session(client_id, redirect_uri=redirect_uri)
    else:
        gitlab = OAuth2Session(client_id, token=json.loads(request.user.gitlabauthorisation.token.replace("'", '"')))
    return gitlab


def gitlab_auth_redirect(request):
    gitlab = get_gitlab()
    token_url = 'http://185.22.60.142:8889/oauth/token'
    client_secret = r'b3d2981b461dded4655810765b2e898ced9fd55a277348a1502607960da5c1f2'
    gitlab.fetch_token(token_url, client_secret=client_secret, code=request.GET['code'])

    r = gitlab.get("http://185.22.60.142:8889/api/v3/user")

    user_json = json.loads(r.content.decode("utf-8"))
    print(user_json)

    try:
        user = User.objects.get(gitlabauthorisation__gitlab_user_id=user_json['id'])
    except ObjectDoesNotExist:
        user = User()
        user.username = "gitlab_" + str(user_json["id"])
        user.save()
        user.gitlabauthorisation = GitlabAuthorisation()

    user.gitlabauthorisation.gitlab_user_id = user_json["id"]
    user.gitlabauthorisation.token = gitlab.token
    user.gitlabauthorisation.save()

    user.backend = 'django.contrib.auth.backends.ModelBackend'
    django_login(request, user)

    return HttpResponseRedirect('/')


def login_redirect(request):
    gitlab = get_gitlab()
    authorization_base_url = 'http://185.22.60.142:8889/oauth/authorize'
    authorization_url, state = gitlab.authorization_url(authorization_base_url)
    return HttpResponseRedirect(authorization_url)


class Login(TemplateView):
    template_name = "HuskyJamGuru/login.html"
