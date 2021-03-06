from django.contrib import admin
from django.forms import ModelForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from .models import Project, GitlabProject, UserToProjectAccess, GitlabAuthorisation, GitLabIssue, GitLabMilestone, \
    GitLabBuild, GitLabMR, IssueTypeUpdate, PersonalDayWorkPlan, WorkTimeEvaluation, IssueTimeSpentRecord,\
    PersonalNotification


class UserToProjectAccessForm(ModelForm):

    class Meta:
        model = UserToProjectAccess
        fields = ['user', 'project', 'type']

    def __init__(self, *args, **kwargs):
        super(UserToProjectAccessForm, self).__init__(*args, **kwargs)

        choices = []
        users = get_user_model().objects.all()
        for user in users:
            try:
                user_name = user.gitlabauthorisation.name + "(" + user.gitlabauthorisation.username + ")"
            except ObjectDoesNotExist:
                user_name = user.username
            choices.append(
                (user.pk, user_name)
            )
        self.fields['user'].choices = choices


class UserToProjectAccessInline(admin.TabularInline):
    form = UserToProjectAccessForm
    model = UserToProjectAccess
    extra = 0


admin.site.register(GitlabProject)
admin.site.register(UserToProjectAccess)


class ProjectAdmin(admin.ModelAdmin):
    inlines = [
        UserToProjectAccessInline,
    ]

admin.site.register(Project, ProjectAdmin)


admin.site.register(GitlabAuthorisation)
admin.site.register(GitLabMilestone)
admin.site.register(GitLabIssue)
admin.site.register(GitLabBuild)
admin.site.register(GitLabMR)
admin.site.register(IssueTypeUpdate)
admin.site.register(PersonalNotification)
admin.site.register(PersonalDayWorkPlan)
admin.site.register(WorkTimeEvaluation)
admin.site.register(IssueTimeSpentRecord)
