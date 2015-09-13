from requests_oauthlib import OAuth2Session
from django.contrib.auth import login as django_login
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.conf import settings

import json

from HuskyJamGuru.models import GitlabAuthorisation, GitlabProject, GitLabMilestone, GitLabIssue


def get_gitlab(request=None, redirect_uri=''):
    client_id = settings.GITLAB_APPLICATION_ID
    if request is None:

        gitlab = OAuth2Session(client_id, redirect_uri=redirect_uri)
    else:
        gitlab = OAuth2Session(client_id, token=json.loads(request.user.gitlabauthorisation.token.replace("'", '"')))
    return gitlab


def gitlab_auth_callback(request):
    redirect_uri = 'http://' + request.get_host() + str(reverse_lazy('gitlab_auth_callback'))
    gitlab = get_gitlab(redirect_uri=redirect_uri)
    token_url = settings.GITLAB_URL + '/oauth/token'
    client_secret = settings.GITLAB_APPLICATION_SECRET
    gitlab.fetch_token(token_url, client_secret=client_secret, code=request.GET['code'])

    r = gitlab.get("http://185.22.60.142:8889/api/v3/user")

    user_json = json.loads(r.content.decode("utf-8"))

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
    user.gitlabauthorisation.token = gitlab.token
    user.gitlabauthorisation.save()

    user.backend = 'django.contrib.auth.backends.ModelBackend'
    django_login(request, user)

    return HttpResponseRedirect(reverse('HuskyJamGuru:project-list'))


def login_redirect(request):
    redirect_uri = 'http://' + request.get_host() + str(reverse_lazy('gitlab_auth_callback'))
    gitlab = get_gitlab(redirect_uri=redirect_uri)
    authorization_base_url = settings.GITLAB_URL + '/oauth/authorize'
    authorization_url, state = gitlab.authorization_url(authorization_base_url)
    return HttpResponseRedirect(authorization_url)


def load_new_and_update_existing_projects_from_gitlab(request):
    projects = json.loads(
        get_gitlab(request).get(settings.GITLAB_URL + "/api/v3/projects").content.decode("utf-8")
    )
    for project in projects:
        gitlab_project = GitlabProject.objects.get_or_create(gitlab_id=project['id'])[0]
        gitlab_project.name = project['name']
        gitlab_project.name_with_namespace = project['name_with_namespace']
        gitlab_project.save()
        milestones = json.loads(
            get_gitlab(request).get(
                settings.GITLAB_URL + "/api/v3/projects/" + str(gitlab_project.gitlab_id) + "/milestones"
            ).content.decode("utf-8")
        )
        for milestone in milestones:
            print(milestone)
            gitlab_milestone = GitLabMilestone.objects.get_or_create(
                gitlab_milestone_id=milestone['iid'],
                gitlab_project=gitlab_project
            )[0]
            gitlab_milestone.name = milestone['title']
            gitlab_milestone.save()

        issues = json.loads(
            get_gitlab(request).get(
                settings.GITLAB_URL + "/api/v3/projects/" + str(gitlab_project.gitlab_id) + "/issues"
            ).content.decode("utf-8")
        )
        for issue in issues:
            gitlab_issue = GitLabIssue.objects.get_or_create(
                gitlab_issue_id=issue['id'],
                gitlab_project=gitlab_project
            )[0]
            gitlab_issue.name = issue['title']
            gitlab_issue.gitlab_milestone = GitLabMilestone.objects.get(
                gitlab_milestone_id=issue['milestone']['iid'],
                gitlab_project=gitlab_project
            )
            gitlab_issue.description = issue['description']
            gitlab_issue.gitlab_issue_iid = issue['iid']
            gitlab_issue.updated_at = issue['updated_at']
            gitlab_issue.project = gitlab_project
            gitlab_issue.save()