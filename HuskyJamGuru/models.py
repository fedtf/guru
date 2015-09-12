from django.db import models
from django.conf import settings
from django.db.models import Q
from django.contrib.auth.models import User


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
        return Project.objects.filter(user_project_accesses__in=UserToProjectAccess.objects.filter(user=user).all())


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


class Task(GitlabModelExtension):
    name = models.CharField(max_length=500, default="Can not load =(")
