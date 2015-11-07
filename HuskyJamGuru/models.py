import datetime
import json
import logging

from django.utils.functional import cached_property
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from django.core.urlresolvers import reverse

from requests_oauthlib import OAuth2Session
from celery.contrib.methods import task_method
from multiselectfield import MultiSelectField

from Project.celery import app


logger = logging.getLogger(__name__)


class GitlabSynchronizeMixin(object):
    @classmethod
    def gitlab(cls):
        superuser = get_user_model().objects.filter(is_superuser=True).first()
        return OAuth2Session(settings.GITLAB_APPLICATION_ID,
                             token=json.loads(superuser.gitlabauthorisation.token.replace("'", '"')))

    @classmethod
    def pull_from_gitlab(cls, request_path):
        response = cls.gitlab().get('{}/api/v3/{}'.format(settings.GITLAB_URL, request_path))
        if response.status_code == 200:
            data = json.loads(response.content.decode('utf-8'))
            if type(data) != list:
                data = [data]
            return data
        else:
            logger.warning(("Gitlab api returned not 200, "
                            "it returned {} with reason {} on {}").format(response.status_code,
                                                                          response.reason,
                                                                          request_path))
            return []

    @classmethod
    def push_to_gitlab(cls, request_path, push_data, type='update'):
        if type == 'update':
            return cls.gitlab().put('{}/api/v3/{}'.format(settings.GITLAB_URL, request_path), push_data)
        elif type == 'create':
            return cls.gitlab().post('{}/api/v3/{}'.format(settings.GITLAB_URL, request_path), push_data)


class WorkTimeEvaluation(models.Model):

    TYPE_CHOICES = (
        ('markup', 'Markup'),
        ('backend', 'Backend'),
        ('testing', 'Testing'),
        ('ux', 'UX'),
        ('business-analyse', 'Business Analyse'),
        ('design', 'Design'),
        ('management', 'Management'),
    )

    project = models.ForeignKey('Project', related_name="work_time_evaluation")
    type = models.CharField(max_length=100, choices=TYPE_CHOICES)
    time = models.IntegerField()


class Project(models.Model):
    STATUS_CHOISES = (
        ('presale', 'Presale'),
        ('in-development', 'In development'),
        ('finished', 'Finished'),
    )

    name = models.CharField(max_length=500, default="")
    status = models.CharField(
        max_length=100, choices=STATUS_CHOISES, blank=False, null=False, default=STATUS_CHOISES[0]
    )
    creation_date = models.DateField(auto_now=True)
    work_start_date = models.DateField(null=True, blank=True)
    deadline_date = models.DateField(null=True, blank=True)
    issues_types = models.TextField(default='open, in progress, fixed, verified')

    @app.task(filter=task_method, name="Project.update_from_gitlab")
    def update_from_gitlab(self):
        for gitlab_project in self.gitlab_projects.all():
            gitlab_project.update_from_gitlab()

    @cached_property
    def issues(self):
        issues = GitLabIssue.objects.none()
        gitlab_projects = self.gitlab_projects.all()
        for gitlab_project in gitlab_projects:
            issues = issues | gitlab_project.issues.all()
        return issues

    @cached_property
    def developers(self):
        developers = []
        accesses = UserToProjectAccess.objects.filter(project=self, type='developer').all()
        for access in accesses:
            developers.append(access.user)
        return developers

    @cached_property
    def users(self):
        users = []
        accesses = UserToProjectAccess.objects.filter(project=self).all()
        for access in accesses:
            users.append(access.user)
        return users

    @cached_property
    def report_list(self):
        report_list = []
        verified = 0
        issues_number = self.issues.count()
        if self.deadline_date is None:
            end_date = timezone.now().date()
        else:
            end_date = min(timezone.now().date(), self.deadline_date)
        for i in range((end_date - self.work_start_date).days + 1):
            date = self.work_start_date + datetime.timedelta(days=i)
            verified += self.issues_type_updates.filter(time__contains=date,
                                                        type='verified').count()
            report_list.append({'date': date, 'issues': issues_number - verified})
        return report_list

    @cached_property
    def issues_types_tuple(self):
        external_list = [type.strip().title() for type in self.issues_types.split(',')]
        internal_list = [type.strip().replace(' ', '_') for type in self.issues_types.split(',')]
        return tuple(zip(internal_list, external_list))

    @cached_property
    def summary_work_time_evaluated_time_in_hours(self):
        summary = 0
        work_time_evaluations = WorkTimeEvaluation.objects.filter(project=self).all()
        for work_time_evaluation in work_time_evaluations:
            summary += work_time_evaluation.time
        return summary

    @cached_property
    def finish_time_evaluation_based_on_work_time_evaluation(self):
        if self.work_start_date < timezone.datetime.today().date():
            medium_work_time_per_day_summ = 0
            developers = self.developers
            for developer in developers:
                medium_work_time_per_day_summ += self.get_user_work_time(
                    developer, None, self.work_start_date, timezone.datetime.today().date()
                )
            project_work_days_amount = (timezone.datetime.today().date() - self.work_start_date).days
            medium_work_time_per_day = round(medium_work_time_per_day_summ / 60) / project_work_days_amount
            hours_left = self.summary_work_time_evaluated_time_in_hours - medium_work_time_per_day_summ / 60
            days_left = hours_left / medium_work_time_per_day
            return timezone.datetime.today().date() + datetime.timedelta(days=days_left)

    def __str__(self):
        return self.name

    def get_user_work_time(self, user, date, from_date=None, to_date=None):
        time = timezone.timedelta()
        if from_date is None or to_date is None:
            from_date = date
            to_date = date
        min_time = datetime.datetime.combine(from_date, datetime.datetime.min.time())
        max_time = datetime.datetime.combine(to_date, datetime.datetime.max.time())
        time_records = IssueTimeSpentRecord.objects.filter(
            user=user,
            gitlab_issue__gitlab_project__project=self,
            time_start__range=(min_time, max_time),
            time_stop__range=(min_time, max_time)
        ).all()
        for time_record in time_records:
            time += time_record.time_interval

        tasks_in_progress = IssueTypeUpdate.objects.filter(
            project=self, is_current=True, type='in_progress', author=user,
            time__gte=timezone.make_aware(
                datetime.datetime.combine(from_date, datetime.datetime.min.time()),
                timezone.get_default_timezone()
            ),
            time__lte=timezone.now(),
        ).all()

        result = {
            'time': None,
            'working_now': False
        }
        if len(tasks_in_progress) > 0:
            for task_in_progress in tasks_in_progress:
                if task_in_progress.time >= timezone.make_aware(
                    datetime.datetime.combine(from_date, datetime.datetime.min.time()),
                    timezone.get_default_timezone()
                ):
                    if timezone.now() <= timezone.make_aware(
                        datetime.datetime.combine(to_date, datetime.datetime.max.time()),
                        timezone.get_default_timezone()
                    ):
                        result['working_now'] = True
                        time += timezone.now() - task_in_progress.time
        result['time'] = time
        return result

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

    def __str__(self):
        try:
            user_name = self.user.gitlabauthorisation.name + "(" + self.user.gitlabauthorisation.username + ")"
        except ObjectDoesNotExist:
            user_name = self.user.username
        return self.get_type_display() + ": " + user_name + " in " + self.project.name


class GitlabAuthorisation(models.Model):
    user = models.OneToOneField(User)
    gitlab_user_id = models.IntegerField(unique=True, blank=None)
    token = models.CharField(max_length=500)
    name = models.CharField(max_length=500, unique=False, blank=True)
    username = models.CharField(max_length=500, unique=False, blank=True)

    @property
    def user_projects_issues_statistics(self):
        # Returns the dictionary with the numbers of
        # all open and (open and unassigned) issues
        # in all projects that user has access to.
        user_projects_issues_statistics = {'open': 0, 'unassigned': 0}

        for project_access in self.user.to_project_accesses.all():
            for issue in project_access.project.issues.all():
                if issue.current_type.type == 'open':
                    user_projects_issues_statistics['open'] += 1
                    if not issue.assignee:
                        user_projects_issues_statistics['unassigned'] += 1
        return user_projects_issues_statistics

    @property
    def weekly_time_spent_records(self):
        weekly_records = []
        records = self.user.issues_time_spent_records.all()

        if records:
            earliest_record = records.last()
            monday_of_first_week = earliest_record.time_start.date() - \
                timezone.timedelta(days=earliest_record.time_start.weekday())
            for i in range(0, (timezone.now().date() - monday_of_first_week).days + 1, 7):
                start_date = monday_of_first_week + timezone.timedelta(days=i)
                end_date = start_date + timezone.timedelta(days=6)
                week_records = records.filter(
                    time_start__gte=timezone.make_aware(
                        datetime.datetime.combine(
                            start_date, timezone.datetime.min.time()
                        ), timezone.get_current_timezone()
                    ),
                    time_start__lte=timezone.make_aware(
                        datetime.datetime.combine(
                            end_date, timezone.datetime.max.time()
                        ), timezone.get_current_timezone()
                    )
                )

                week = {}
                week['start_date'] = start_date
                week['end_date'] = end_date
                week['records'] = week_records
                weekly_records.append(week)

            weekly_records.reverse()
        return weekly_records

    @property
    def current_issue(self):
        all_user_issues = GitLabIssue.objects.filter(assignee=self).all()
        for issue in all_user_issues:
            if issue.current_type.type == 'in_progress':
                return issue
        return None

    def to_project_access_types(self, project):
        return [access.type for access in UserToProjectAccess.objects.filter(
                user=self.user, project=project).all()]


class GitlabModelExtension(models.Model):
    gitlab_id = models.IntegerField(unique=True, blank=None)


class GitlabProject(GitlabSynchronizeMixin, GitlabModelExtension):
    name = models.CharField(max_length=500, unique=False, blank=True)
    name_with_namespace = models.CharField(max_length=500, unique=False, blank=True)
    project = models.ForeignKey('Project', related_name='gitlab_projects', null=True, blank=True)
    path_with_namespace = models.CharField(max_length=500, unique=False, blank=True)

    @classmethod
    def pull_from_gitlab(cls, request_path='projects'):
        projects = super(GitlabProject, cls).pull_from_gitlab(request_path)
        for project in projects:
            gitlab_project = GitlabProject.objects.get_or_create(gitlab_id=project['id'])[0]
            gitlab_project.name = project['name']
            gitlab_project.path_with_namespace = project['path_with_namespace']
            gitlab_project.name_with_namespace = project['name_with_namespace']
            gitlab_project.creation_time = project['created_at']
            gitlab_project.save()

    @app.task(filter=task_method, name="GitlabProject.update_from_gitlab")
    def update_from_gitlab(self):
        GitlabProject.pull_from_gitlab('projects/{}'.format(self.gitlab_id))
        GitLabMilestone.pull_from_gitlab('projects/{}/milestones'.format(self.gitlab_id))
        GitLabIssue.pull_from_gitlab('projects/{}/issues'.format(self.gitlab_id))

    @property
    def gitlab_opened_milestones(self):
        return self.gitlab_milestones.filter(closed=False).all()

    @property
    def create_milestone_link(self):
        return '{}/{}/milestones/new'.format(settings.GITLAB_URL, self.path_with_namespace)

    def __str__(self):
        return self.name_with_namespace


class GitLabMilestone(GitlabSynchronizeMixin, models.Model):
    gitlab_milestone_id = models.IntegerField(unique=False, blank=None)
    gitlab_milestone_iid = models.IntegerField(unique=False, blank=None)
    gitlab_project = models.ForeignKey('GitlabProject', unique=False, blank=None, related_name='gitlab_milestones')
    name = models.CharField(max_length=500, unique=False, blank=True)
    closed = models.BooleanField(default=False)
    priority = models.IntegerField(editable=False)
    rolled_up = models.BooleanField(default=False)  # True если администратор свернул майлстоун на странице проекта

    def save(self, *args, **kwargs):
        if self.pk is None:
            last_milestone = self.gitlab_project.gitlab_milestones.last()
            if last_milestone is not None:
                self.priority = last_milestone.priority + 1
            else:
                self.priority = 1
        super(GitLabMilestone, self).save(*args, **kwargs)

    @classmethod
    def pull_from_gitlab(cls, request_path='milestones'):
        if request_path == 'milestones':
            for gitlab_project in GitlabProject.objects.all():
                # No api endpoint for getting all milestones without projects.
                milestones = super(GitLabMilestone, cls).pull_from_gitlab('projects/{}/milestones'
                                                                          .format(gitlab_project.gitlab_id))
        else:
            milestones = super(GitLabMilestone, cls).pull_from_gitlab(request_path)
        for milestone in milestones:
            gitlab_milestone = GitLabMilestone.objects.get_or_create(
                gitlab_milestone_id=milestone['id'],
                gitlab_milestone_iid=milestone['iid'],
                gitlab_project=GitlabProject.objects.get(gitlab_id=milestone['project_id'])
            )[0]
            gitlab_milestone.name = milestone['title']
            gitlab_milestone.closed = milestone['state'] != 'active'
            gitlab_milestone.save()

    @app.task(filter=task_method, name="GitLabMilestone.update_from_gitlab")
    def update_from_gitlab(self):
        GitLabMilestone.pull_from_gitlab('projects/{}/milestones/{}'
                                         .format(self.gitlab_project.gitlab_id,
                                                 self.gitlab_milestone_id))
        GitLabIssue.pull_from_gitlab('projects/{}/issues?milestone={}'
                                     .format(self.gitlab_project.gitlab_id,
                                             self.name))

    @property
    def create_issue_link(self):
        return '{}/{}/issues/new?issue%5Bmilestone_id%5D={}'.format(settings.GITLAB_URL,
                                                                    self.gitlab_project.path_with_namespace,
                                                                    self.gitlab_milestone_id)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return '{}#{}'.format(self.gitlab_project.project.get_absolute_url(), self.pk)

    class Meta:
        ordering = ['priority']


class GitLabIssue(GitlabSynchronizeMixin, models.Model):
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

    @classmethod
    def pull_from_gitlab(cls, request_path='issues'):
        issues = super(GitLabIssue, cls).pull_from_gitlab(request_path)
        for issue in issues:
            gitlab_issue = GitLabIssue.objects.get_or_create(
                gitlab_issue_iid=issue['iid'],
                gitlab_issue_id=issue['id'],
                gitlab_project=GitlabProject.objects.get(gitlab_id=issue['project_id'])
            )[0]
            gitlab_issue.name = issue['title']
            if issue['milestone'] is not None:
                gitlab_issue.gitlab_milestone = GitLabMilestone.objects.get(
                    gitlab_milestone_id=issue['milestone']['id'],
                )
            else:
                gitlab_issue.gitlab_milestone = None
            if issue['assignee'] is not None:
                try:
                    gitlab_issue.assignee = GitlabAuthorisation.objects.get(gitlab_user_id=issue['assignee']['id'])
                except ObjectDoesNotExist:
                    pass
            else:
                gitlab_issue.assignee = None
            gitlab_issue.description = issue['description']
            gitlab_issue.updated_at = issue['updated_at']
            gitlab_issue.save()

    @app.task(filter=task_method, name="GitLabIssue.update_from_gitlab")
    def update_from_gitlab(self):
        GitLabIssue.pull_from_gitlab('projects/{}/issues/{}'.format(self.gitlab_project.gitlab_id,
                                                                    self.gitlab_issue_id))

    def reassign_to_user(self, user):
        data = {
            'assignee_id': user.gitlabauthorisation.gitlab_user_id,
        }
        GitLabIssue.push_to_gitlab('projects/{}/issues/{}'.format(self.gitlab_project.gitlab_id,
                                                                  self.gitlab_issue_id,), data)

    def change_state_in_gitlab(self, new_state):
        data = {
            'state_event': new_state,
        }
        GitLabIssue.push_to_gitlab('projects/{}/issues/{}'.format(self.gitlab_project.gitlab_id,
                                                                  self.gitlab_issue_id,), data)

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
    def spent_time(self):
        time = timezone.timedelta()
        for time_spent_record in IssueTimeSpentRecord.objects.filter(gitlab_issue=self).all():
            time += time_spent_record.time_interval

        if self.current_type.type == 'in_progress':
            time += timezone.now() - IssueTypeUpdate.objects.filter(gitlab_issue=self).order_by('-pk')[0:1].get().time
        return time

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
    time_stop = models.DateTimeField(auto_now=True)

    @property
    def time_interval(self):
        return self.time_stop - self.time_start

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
                )
                new_issue_time_spent_record.save()
            for previous in IssueTypeUpdate.objects.filter(gitlab_issue=self.gitlab_issue, is_current=True):
                previous.is_current = False
                previous.save()

        self.project = self.gitlab_issue.gitlab_project.project
        super(IssueTypeUpdate, self).save(*args, **kwargs)


class TelegramUser(models.Model):
    EVENTS = (
        ('issue_create', 'Issue Opening'),
        ('issue_close', 'Issue Closing'),
        ('note', 'New Comments'),
        ('push', 'Push Events'),
    )

    user = models.OneToOneField(User, related_name='telegram_user')
    telegram_id = models.CharField(max_length=50, blank=True)
    notification_events = MultiSelectField(choices=EVENTS, blank=True)
    notification_enabled = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class PersonalDayWorkPlan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    date = models.DateField()
    work_hours = models.IntegerField()
    creation_time = models.DateTimeField(auto_now=True)
    is_actual = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.is_actual:
            actual_previous = PersonalDayWorkPlan.objects.filter(
                user=self.user,
                date=self.date,
                is_actual=True
            )
            if self.id:
                actual_previous.filter(creation_time__lt=self.creation_time)
            actual_previous = actual_previous.all()
            for previous in actual_previous:
                if previous is not self:
                    previous.is_actual = False
                    previous.save()
        return super(PersonalDayWorkPlan, self).save(*args, **kwargs)

    @staticmethod
    def get_work_plan(user, from_date, to_date):
        work_plans_per_day = PersonalDayWorkPlan.objects.filter(
            user=user,
            date__gte=from_date,
            date__lte=to_date,
            is_actual=True
        ).order_by('creation_time').all()
        return work_plans_per_day

    @staticmethod
    def get_amount_of_unceasingly_planned_days(user, from_date):
        work_plans_per_day = PersonalDayWorkPlan.objects.filter(
            user=user,
            is_actual=True
        ).filter(date__gte=from_date).order_by('date').all()
        days = 0
        day_without_plan_found = False
        last_day = from_date
        for work_plan in work_plans_per_day:
            if not day_without_plan_found and last_day != work_plan.date:
                if last_day + datetime.timedelta(days=1) < work_plan.date:
                    day_without_plan_found = True
                else:
                    days += 1
                    last_day = work_plan.date
        return days
