import datetime

from django.utils.functional import cached_property
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from django.core.urlresolvers import reverse


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

    @property
    def issues(self):
        issues = GitLabIssue.objects.none()
        gitlab_projects = self.gitlab_projects.all()
        for gitlab_project in gitlab_projects:
            # will not work for sliced querysets
            issues = issues | gitlab_project.issues.all()
        return issues

    @property
    def developers(self):
        developers = []
        accesses = UserToProjectAccess.objects.filter(project=self, type='developer').all()
        for access in accesses:
            developers.append(access.user)
        return developers

    @property
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

    @property
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
        seconds = 0
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
            seconds += time_record.seconds
        return round(seconds / 60)

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
        # all open and open and unassigned issues
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
                    time_start__lte=
                    timezone.make_aware(
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


class GitlabProject(GitlabModelExtension):
    name = models.CharField(max_length=500, unique=False, blank=True)
    name_with_namespace = models.CharField(max_length=500, unique=False, blank=True)
    project = models.ForeignKey('Project', related_name='gitlab_projects', null=True, blank=True)
    path_with_namespace = models.CharField(max_length=500, unique=False, blank=True)

    @property
    def gitlab_opened_milestones(self):
        return self.gitlab_milestones.filter(closed=False).all()

    @property
    def create_milestone_link(self):
        return '{}/{}/milestones/new'.format(settings.GITLAB_URL, self.path_with_namespace)

    def __str__(self):
        return self.name_with_namespace


class GitLabMilestone(models.Model):
    gitlab_milestone_id = models.IntegerField(unique=False, blank=None)
    gitlab_milestone_iid = models.IntegerField(unique=False, blank=None)
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
    time_stop = models.DateTimeField(auto_now=True)

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
                )
                new_issue_time_spent_record.save()
            for previous in IssueTypeUpdate.objects.filter(gitlab_issue=self.gitlab_issue, is_current=True):
                previous.is_current = False
                previous.save()

        self.project = self.gitlab_issue.gitlab_project.project
        super(IssueTypeUpdate, self).save(*args, **kwargs)


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
