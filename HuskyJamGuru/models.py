from django.db import models

from django.contrib.auth.models import User


class GitlabAuthorisation(models.Model):
    user = models.OneToOneField(User)
    gitlab_user_id = models.IntegerField(unique=True, blank=None)
    token = models.CharField(max_length=500)
    name = models.CharField(max_length=500, unique=False, blank=True)
    username = models.CharField(max_length=500, unique=False, blank=True)


class GitlabModelExtension(models.Model):
    gitlab_id = models.IntegerField(unique=True, blank=None)


class Project(GitlabModelExtension):
    name = models.CharField(max_length=500, default="Can not load =(")


class Task(GitlabModelExtension):
    name = models.CharField(max_length=500, default="Can not load =(")