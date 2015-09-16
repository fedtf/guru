from django.contrib import admin
from .models import Project, GitlabProject, UserToProjectAccess, GitlabAuthorisation, GitLabIssue, GitLabMilestone, \
    GitLabBuild, GitLabMR, IssueTypeUpdate

admin.site.register(Project)
admin.site.register(GitlabProject)
admin.site.register(UserToProjectAccess)
admin.site.register(GitlabAuthorisation)
admin.site.register(GitLabMilestone)
admin.site.register(GitLabIssue)
admin.site.register(GitLabBuild)
admin.site.register(GitLabMR)
admin.site.register(IssueTypeUpdate)
