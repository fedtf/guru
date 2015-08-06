from requests_oauthlib import OAuth2Session
from django.contrib.auth import login as django_login
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

import json

from HuskyJamGuru.models import GitlabAuthorisation


def get_gitlab(request=None):
    client_id = r'9bc472164fc76c3dda596f01205cba2bb63a47d4e57d59fd5dd01762b3042721'
    redirect_uri = 'http://127.0.0.1:8000' + reverse('gitlab_auth_callback')
    if request is None:
        gitlab = OAuth2Session(client_id, redirect_uri=redirect_uri)
    else:
        gitlab = OAuth2Session(client_id, token=json.loads(request.user.gitlabauthorisation.token.replace("'", '"')))
    return gitlab


def gitlab_auth_callback(request):
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
    user.gitlabauthorisation.name = user_json["name"]
    user.gitlabauthorisation.username = user_json["username"]
    print(gitlab.token)
    user.gitlabauthorisation.token = gitlab.token
    user.gitlabauthorisation.save()

    user.backend = 'django.contrib.auth.backends.ModelBackend'
    django_login(request, user)

    return HttpResponseRedirect(reverse('HuskyJamGuru:dashboard'))


def login_redirect(request):
    gitlab = get_gitlab()
    authorization_base_url = 'http://185.22.60.142:8889/oauth/authorize'
    authorization_url, state = gitlab.authorization_url(authorization_base_url)
    return HttpResponseRedirect(authorization_url)
