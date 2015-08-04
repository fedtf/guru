from django.db import models

from django.contrib.auth.models import User


class GitlabAuthorisation(models.Model):
    user = models.OneToOneField(User)
    gitlab_user_id = models.IntegerField(unique=True, blank=None)
    token = models.CharField(max_length=500)
    token_time = models.IntegerField(default=0)
    update_token = models.CharField(max_length=500)


class Project(models.Model):
    gitlab_id = models.IntegerField(unique=True, blank=None)
    name = models.CharField(max_length=500, default="Can not load =(")