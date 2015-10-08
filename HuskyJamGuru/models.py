import datetime

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from django.core.urlresolvers import reverse


class Project(models.Model):
    name = models.CharField(max_length=500, default="")
    creation_date = models.DateField()
    finish_date_assessment = models.DateField()
    issues_types = models.TextField(default='open, in progress, fixed, verified')

    @property
    def issues(self):
        issues = GitLabIssue.objects.none()
        gitlab_projects = self.gitlab_projects.all()
        for gitlab_project in gitlab_projects:
            # will not work for sliced querysets
            issues = issues | gitlab_project.issues.all()
        return issues

    @property
    def report_list(self):
        report_list = []
        closed = 0
        issues_number = self.issues.count()
        end_date = min(timezone.now().date(), self.finish_date_assessment)
        for i in range((end_date - self.creation_date).days + 1):
            date = self.creation_date + datetime.timedelta(days=i)
            closed += self.issues_type_updates.filter(time__contains=date,
                                                      type='closed').count()
            report_list.append({'date': date, 'issues': issues_number - closed})
        return report_list

    @property
    def issues_types_tuple(self):
        external_list = [type.strip().title() for type in self.issues_types.split(',')]
        internal_list = [type.strip().replace(' ', '_') for type in self.issues_types.split(',')]
        return tuple(zip(internal_list, external_list))

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('HuskyJamGuru:project-detail', kwargs={'pk': self.pk})


class UserToProjectAccess(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="to_project_accesses")
    project = models.ForeignKey(Project, related_name="user_project_accesses")

    TYPE_CHOICES = (
        ('administrator', 'Administrator'),
        ('developer', 'Developer'),
        ('manager', 'Manager'),
    )

    type = models.CharField(max_length=100, choices=TYPE_CHOICES)

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

    @property
    def user_projects_issues_statistics(self):
        user_projects_issues_statistics = {'open': 0, 'unassigned': 0}

        for project_access in self.user.to_project_accesses.all():
            for issue in project_access.project.issues.all():
                if issue.current_type.type == 'open':
                    user_projects_issues_statistics['open'] += 1
                    if not issue.assignee:
                        user_projects_issues_statistics['unassigned'] += 1
        return user_projects_issues_statistics

    @property
    def current_issue(self):
        all_user_issues = GitLabIssue.objects.filter(assignee=self).all()
        for issue in all_user_issues:
            if issue.current_type.type == 'in_progress':
                return issue
        return None


class GitlabModelExtension(models.Model):
    gitlab_id = models.IntegerField(unique=True, blank=None)


class GitlabProject(GitlabModelExtension):
    name = models.CharField(max_length=500, unique=False, blank=True)
    name_with_namespace = models.CharField(max_length=500, unique=False, blank=True)
    project = models.ForeignKey('Project', related_name='gitlab_projects', null=True, blank=True)
    path_with_namespace = models.CharField(max_length=500, unique=False, blank=True)

    @property
    def gitlab_opened_milestones(self):
        return self.gitlab_milestones.filter(closed=False).all()

    def __str__(self):
        return self.name_with_namespace


class GitLabMilestone(models.Model):
    gitlab_milestone_id = models.IntegerField(unique=False, blank=None)
    gitlab_project = models.ForeignKey('GitlabProject', unique=False, blank=None, related_name='gitlab_milestones')
    name = models.CharField(max_length=500, unique=False, blank=True)
    closed = models.BooleanField(default=False)
    priority = models.IntegerField(editable=False)

    def save(self, *args, **kwargs):
        if self.pk is None:
            last_milestone = self.gitlab_project.gitlab_milestones.last()
            if last_milestone is not None:
                self.priority = last_milestone.priority + 1
            else:
                self.priority = 1
        super(GitLabMilestone, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return '{}#{}'.format(self.gitlab_project.project.get_absolute_url(), self.pk)

    class Meta:
        ordering = ['priority']


class GitLabIssue(models.Model):
    gitlab_issue_id = models.IntegerField(unique=False, blank=None)
    gitlab_project = models.ForeignKey('GitlabProject', unique=False, blank=None, related_name='issues')

    gitlab_issue_iid = models.IntegerField(unique=False, blank=None)
    gitlab_milestone = models.ForeignKey('GitLabMilestone', unique=False, blank=True, null=True)
    name = models.CharField(max_length=500, unique=False, blank=True)
    description = models.CharField(max_length=1000, unique=False, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    assignee = models.ForeignKey('GitlabAuthorisation', unique=False, blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def current_type(self):
        try:
            c_type = IssueTypeUpdate.objects.filter(gitlab_issue=self).order_by('-pk')[0:1].get()
            return c_type
        except Exception:
            c_type = IssueTypeUpdate(
                gitlab_issue=self,
                type='open'
            )
            return c_type

    @property
    def is_closed(self):
        return self.current_type.type == 'closed'

    @property
    def closed_at(self):
        if self.is_closed:
            return self.current_type.time.date()
        else:
            return None

    @property
    def spent_minutes(self):
        seconds = 0
        for time_spent_record in IssueTimeSpentRecord.objects.filter(gitlab_issue=self).all():
            seconds += time_spent_record.seconds
        minutes = round(seconds / 60)
        return minutes

    @property
    def link(self):
        return settings.GITLAB_URL + '/' \
            + self.gitlab_project.path_with_namespace + '/issues/' + str(self.gitlab_issue_iid)


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

    @property
    def seconds(self):
        return (self.time_stop - self.time_start).total_seconds()

    class Meta:
        ordering = ['-time_start']


class IssueTypeUpdate(models.Model):
    gitlab_issue = models.ForeignKey(GitLabIssue, related_name='type_updates')
    type = models.CharField(max_length=100)
    author = models.ForeignKey(User, unique=False, null=True, blank=True)
    time = models.DateTimeField(auto_now=True)
    is_current = models.BooleanField(default=True)
    project = models.ForeignKey(Project, editable=False, related_name='issues_type_updates')

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.gitlab_issue.current_type.type == 'in_progress' and self.type != 'in_progress':
                new_issue_time_spent_record = IssueTimeSpentRecord(
                    user=self.gitlab_issue.current_type.author,
                    gitlab_issue=self.gitlab_issue,
                    time_start=self.gitlab_issue.current_type.time,
                    time_stop=datetime.datetime.now()
                )
                new_issue_time_spent_record.save()
            for previous in IssueTypeUpdate.objects.filter(gitlab_issue=self.gitlab_issue, is_current=True):
                previous.is_current = False
                previous.save()

        self.project = self.gitlab_issue.gitlab_project.project
        super(IssueTypeUpdate, self).save(*args, **kwargs)
