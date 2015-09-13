from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.conf import settings


class Project(models.Model):
    name = models.CharField(max_length=500, default="")

    def __str__(self):
        return self.name


class UserToProjectAccess(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="to_project_accesses")
    project = models.ForeignKey(Project, related_name="user_project_accesses")

    TYPE_CHOICES = (
        ('administrator', 'Administrator'),
        ('developer', 'Developer'),
    )

    type = models.CharField(max_length=100)

    @staticmethod
    def get_projects_queryset_user_has_access_to(user, access='developer'):
        if not user.is_anonymous():
            return Project.objects.filter(user_project_accesses__in=UserToProjectAccess.objects.filter(user=user).all())
        else:
            return None


class GitlabAuthorisation(models.Model):
    user = models.OneToOneField(User)
    gitlab_user_id = models.IntegerField(unique=True, blank=None)
    token = models.CharField(max_length=500)
    name = models.CharField(max_length=500, unique=False, blank=True)
    username = models.CharField(max_length=500, unique=False, blank=True)


class GitlabModelExtension(models.Model):
    gitlab_id = models.IntegerField(unique=True, blank=None)


class GitlabProject(GitlabModelExtension):
    name = models.CharField(max_length=500, unique=False, blank=True)
    name_with_namespace = models.CharField(max_length=500, unique=False, blank=True)
    project = models.ForeignKey('Project', related_name='gitlab_projects', null=True, blank=True)

    def __str__(self):
        return self.name_with_namespace


class GitLabMilestone(models.Model):
    gitlab_milestone_id = models.IntegerField(unique=False, blank=None)
    gitlab_project = models.ForeignKey('GitlabProject', unique=False, blank=None, related_name='gitlab_milestones')
    name = models.CharField(max_length=500, unique=False, blank=True)

    def __str__(self):
        return self.name


class GitLabIssue(models.Model):
    gitlab_issue_id = models.IntegerField(unique=False, blank=None)
    gitlab_project = models.ForeignKey('GitlabProject', unique=False, blank=None, related_name='issues')

    gitlab_issue_iid = models.IntegerField(unique=False, blank=None)
    gitlab_milestone = models.ForeignKey('GitLabMilestone', unique=False, blank=True, null=True)
    name = models.CharField(max_length=500, unique=False, blank=True)
    description = models.CharField(max_length=1000, unique=False, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class GitLabMR(GitlabModelExtension):
    name = models.CharField(max_length=500, unique=False, blank=True)
    milestone = models.ForeignKey('GitLabMilestone', unique=False, blank=True, null=True)

    def __str__(self):
        return self.name


class GitLabBuild(GitlabModelExtension):
    gitlab_mr = models.ForeignKey('GitLabMilestone', related_name='gitlab_builds')
    author = models.ForeignKey('GitlabAuthorisation', related_name='gitlab_builds')
    test_link = models.CharField(max_length=500, unique=False, blank=True, null=True)
    time = models.DateTimeField()


class IssueTimeAssessment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='issues_assessments')
    gitlab_issue = models.ForeignKey(GitLabIssue, related_name='assessments')
    minutes = models.IntegerField()


class IssueTimeSpentRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='issues_time_spent_records')
    gitlab_issue = models.ForeignKey(GitLabIssue, related_name='time_spent_records')
    time_start = models.DateTimeField()
    time_stop = models.DateTimeField(blank=True, null=True)
