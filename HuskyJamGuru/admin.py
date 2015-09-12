from django.contrib import admin
from .models import Project, GitlabProject, UserToProjectAccess, GitlabAuthorisation

admin.site.register(Project)
admin.site.register(GitlabProject)
admin.site.register(UserToProjectAccess)
admin.site.register(GitlabAuthorisation)