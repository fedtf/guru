import datetime
from mock import patch

from django.test import TestCase
from django.core.urlresolvers import resolve, reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.auth.forms import AuthenticationForm

from .views import ProjectDetailView, WorkReportListView, ProjectReportView, LoginAsGuruUserView, \
    ProjectUpdateView, PersonalTimeReportView
from .models import Project, IssueTypeUpdate, GitlabProject, GitLabIssue, GitLabMilestone, \
    UserToProjectAccess, GitlabAuthorisation, IssueTimeSpentRecord, PersonalDayWorkPlan


def create_data():
    # creates test data for tests
    project = Project(name='testproject', creation_date=timezone.now(),
                      work_start_date=timezone.now())
    project.save()

    gitlab_project = GitlabProject(name='gitlabtestproject', gitlab_id=4,
                                   project=project)
    gitlab_project.save()

    mile1 = GitLabMilestone(name='mile1', gitlab_project=gitlab_project,
                            gitlab_milestone_id=1, gitlab_milestone_iid=2)
    mile1.save()

    mile2 = GitLabMilestone(name='mile2', gitlab_project=gitlab_project,
                            gitlab_milestone_id=2, gitlab_milestone_iid=3)
    mile2.save()

    mile3 = GitLabMilestone(name='mile3', gitlab_project=gitlab_project,
                            gitlab_milestone_id=3, gitlab_milestone_iid=4)
    mile3.save()

    return (mile1, mile2, mile3)


class ProjectDetailTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(username='test', password='testpass',
                                                              email='testadmin@example.com')
        self.client.login(username='test', password='testpass')
        self.mile, _, _ = create_data()
        new_project = self.mile.gitlab_project.project
        self.gitlab_auth = GitlabAuthorisation.objects.create(user=self.user, gitlab_user_id=5, token='blablabla')
        self.project = new_project
        self.page_url = '/project-detail/{}/'.format(self.project.pk)

        self.mocked_time = timezone.datetime(2012, 5, 18, tzinfo=timezone.get_current_timezone())

        def now():
            return self.mocked_time

        patcher = patch('django.utils.timezone.now', now)
        self.addCleanup(patcher.stop)
        patcher.start()

    def test_url_resolves_to_right_view(self):
        found = resolve(self.page_url)
        self.assertEqual(found.func.__name__, ProjectDetailView.__name__)

    def test_page_responds_with_200(self):
        response = self.client.get(self.page_url)
        self.assertEqual(response.status_code, 200)

    def test_page_uses_correct_template(self):
        response = self.client.get(self.page_url)
        self.assertTemplateUsed(response, 'HuskyJamGuru/project_detail.html')

    def test_view_shows_unassigned_milestone_when_necessary(self):
        mile = self.project.gitlab_projects.first().gitlab_milestones.first()
        GitLabIssue.objects.create(gitlab_issue_id=0,
                                   gitlab_project=self.project.gitlab_projects.first(),
                                   gitlab_issue_iid=0,
                                   gitlab_milestone=mile)
        new_issue1 = GitLabIssue.objects.create(gitlab_issue_id=1,
                                                gitlab_project=self.project.gitlab_projects.first(),
                                                gitlab_issue_iid=1)

        response = self.client.get(self.page_url)
        self.assertEqual(response.context['show_unassigned_milestone'], True)

        new_issue1.gitlab_milestone = mile
        new_issue1.save()
        response = self.client.get(self.page_url)
        self.assertEqual(response.context['show_unassigned_milestone'], False)

        GitLabIssue.objects.create(gitlab_issue_id=2,
                                   gitlab_project=self.project.gitlab_projects.first(),
                                   gitlab_issue_iid=2)

        response = self.client.get(self.page_url)
        self.assertEqual(response.context['show_unassigned_milestone'], True)

    def test_view_shows_unassigned_column_when_necessary(self):
        GitLabIssue.objects.create(gitlab_issue_id=0,
                                   gitlab_project=self.project.gitlab_projects.first(),
                                   gitlab_issue_iid=0)
        new_issue1 = GitLabIssue.objects.create(gitlab_issue_id=1,
                                                gitlab_project=self.project.gitlab_projects.first(),
                                                gitlab_issue_iid=1)
        IssueTypeUpdate.objects.create(gitlab_issue=new_issue1,
                                       project=self.project,
                                       type='in_progress')

        response = self.client.get(self.page_url)
        self.assertEqual(response.context['show_unassigned_column'], False)

        new_issue2 = GitLabIssue.objects.create(gitlab_issue_id=2,
                                                gitlab_project=self.project.gitlab_projects.first(),
                                                gitlab_issue_iid=2)
        IssueTypeUpdate.objects.create(gitlab_issue=new_issue2,
                                       project=self.project,
                                       type='unknown')

        response = self.client.get(self.page_url)
        self.assertEqual(response.context['show_unassigned_column'], True)

    def test_create_links_in_response(self):
        gitlab_project = self.project.gitlab_projects.first()
        gitlab_project.path_with_namespace = 'core/proj'
        gitlab_project.save()

        response = self.client.get(self.page_url)
        self.assertContains(response, 'http://185.22.60.142:8889/core/proj/milestones/new')
        new_issue_link = "http://185.22.60.142:8889/core/proj/issues/new?issue%5Bmilestone_id%5D={}"
        new_milestone_gitlab_id = gitlab_project.gitlab_milestones.first().gitlab_milestone_id
        self.assertContains(response, new_issue_link.format(new_milestone_gitlab_id))

    def test_user_work_time(self):
        project = self.mile.gitlab_project.project

        UserToProjectAccess.objects.create(user=self.user, project=project, type='developer')

        issue = GitLabIssue.objects.create(
            gitlab_issue_id=1, gitlab_project=self.mile.gitlab_project, gitlab_issue_iid=1
        )

        self.mocked_time = timezone.datetime(2012, 5, 20, 15, 30, tzinfo=timezone.get_current_timezone())
        issue_type_update = IssueTypeUpdate.objects.create(
            gitlab_issue=issue,
            type='open',
            author=self.user,
            project=self.project
        )

        issue_type_update = IssueTypeUpdate.objects.create(
            gitlab_issue=issue,
            type='in_progress',
            author=self.user,
            project=self.project
        )

        self.mocked_time = timezone.datetime(2012, 5, 20, 15, 35, tzinfo=timezone.get_current_timezone())

        issue_type_update = IssueTypeUpdate.objects.create(
            gitlab_issue=issue,
            type='open',
            author=self.user,
            project=self.project
        )
        #
        # print(issue.spent_minutes)


class WorkReportListTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(username='test', password='testpass',
                                                              email='testadmin@example.com')
        self.client.login(username='test', password='testpass')

    def test_url_resolves_to_work_report_list_view(self):
        found = resolve('/work-report-list/')
        self.assertEqual(found.func.__name__, WorkReportListView.__name__)

    def test_page_responds_with_200(self):
        response = self.client.get('/work-report-list/')
        self.assertEqual(response.status_code, 200)

    def test_page_redirects_to_login_if_not_superuser(self):
        get_user_model().objects.create_user(username='notsuper', password='testpass')
        self.client.login(username='notsuper', password='testpass')
        response = self.client.get('/work-report-list/')
        self.assertRedirects(response, '/login?next=/work-report-list/')

    def test_page_uses_correct_template(self):
        response = self.client.get('/work-report-list/')
        self.assertTemplateUsed(response, 'HuskyJamGuru/work_report_list.html')

    def test_work_report_list_contains_all_users(self):
        get_user_model().objects.create_user(username='testuser1', password='pass')
        get_user_model().objects.create_user(username='testuser2', password='pass')
        response = self.client.get('/work-report-list/')
        self.assertEqual(response.context['user_list'].count(), 3)

    def test_user_projects_issues_statistics(self):
        gitlab_auth = GitlabAuthorisation.objects.create(user=self.user, gitlab_user_id=1, token='asdsgreeg')

        mile, _, _ = create_data()
        new_project = mile.gitlab_project.project

        UserToProjectAccess.objects.create(user=self.user, project=new_project, type='developer')

        issue1 = GitLabIssue.objects.create(gitlab_issue_id=1, gitlab_project=mile.gitlab_project,
                                            gitlab_issue_iid=1)
        issue2 = GitLabIssue.objects.create(gitlab_issue_id=2, gitlab_project=mile.gitlab_project,
                                            gitlab_issue_iid=2)
        GitLabIssue.objects.create(gitlab_issue_id=3, gitlab_project=mile.gitlab_project,
                                   gitlab_issue_iid=3)
        issue4 = GitLabIssue.objects.create(gitlab_issue_id=4, gitlab_project=mile.gitlab_project,
                                            gitlab_issue_iid=4)
        GitLabIssue.objects.create(gitlab_issue_id=5, gitlab_project=mile.gitlab_project,
                                   gitlab_issue_iid=5)
        GitLabIssue.objects.create(gitlab_issue_id=6, gitlab_project=mile.gitlab_project,
                                   gitlab_issue_iid=6)
        self.assertEqual(self.user.gitlabauthorisation.user_projects_issues_statistics, {'open': 6, 'unassigned': 6})

        IssueTypeUpdate.objects.create(gitlab_issue=issue1, type="in_progress", project=new_project)
        self.assertEqual(self.user.gitlabauthorisation.user_projects_issues_statistics, {'open': 5, 'unassigned': 5})

        issue2.assignee = gitlab_auth
        issue2.save()
        self.assertEqual(self.user.gitlabauthorisation.user_projects_issues_statistics, {'open': 5, 'unassigned': 4})

        issue4.assignee = gitlab_auth
        issue4.save()
        self.assertEqual(self.user.gitlabauthorisation.user_projects_issues_statistics, {'open': 5, 'unassigned': 3})

        IssueTypeUpdate.objects.create(gitlab_issue=issue4, type="verified", project=new_project)
        self.assertEqual(self.user.gitlabauthorisation.user_projects_issues_statistics, {'open': 4, 'unassigned': 3})

    def test_user_current_issue(self):
        gitlab_auth = GitlabAuthorisation.objects.create(user=self.user, gitlab_user_id=1, token='asdsgreeg')
        mile, _, _ = create_data()
        new_project = mile.gitlab_project.project

        UserToProjectAccess.objects.create(user=self.user, project=new_project, type='developer')

        issue1 = GitLabIssue.objects.create(gitlab_issue_id=1, gitlab_project=mile.gitlab_project,
                                            gitlab_issue_iid=1)
        GitLabIssue.objects.create(gitlab_issue_id=2, gitlab_project=mile.gitlab_project,
                                   gitlab_issue_iid=2)

        issue1.assignee = gitlab_auth
        issue1.save()

        self.assertEqual(gitlab_auth.current_issue, None)

        IssueTypeUpdate.objects.create(gitlab_issue=issue1, type="in_progress")
        self.assertEqual(gitlab_auth.current_issue, issue1)

    def test_only_six_last_time_records_in_queryset(self):
        mile, _, _ = create_data()

        issue1 = GitLabIssue.objects.create(gitlab_issue_id=1, gitlab_project=mile.gitlab_project,
                                            gitlab_issue_iid=1)
        IssueTimeSpentRecord.objects.create(user=self.user, gitlab_issue=issue1, time_start=timezone.now())
        IssueTimeSpentRecord.objects.create(user=self.user, gitlab_issue=issue1, time_start=timezone.now())
        IssueTimeSpentRecord.objects.create(user=self.user, gitlab_issue=issue1, time_start=timezone.now())
        IssueTimeSpentRecord.objects.create(user=self.user, gitlab_issue=issue1, time_start=timezone.now())
        IssueTimeSpentRecord.objects.create(user=self.user, gitlab_issue=issue1, time_start=timezone.now())
        IssueTimeSpentRecord.objects.create(user=self.user, gitlab_issue=issue1, time_start=timezone.now())
        IssueTimeSpentRecord.objects.create(user=self.user, gitlab_issue=issue1, time_start=timezone.now())

        response = self.client.get('/work-report-list/')

        self.assertEqual(self.user.issues_time_spent_records.all().count(), 7)

        for user in response.context['user_list']:
            self.assertLessEqual(len(user.time_spent_records), 6)


class ProjectReportTest(TestCase):
    def setUp(self):
        get_user_model().objects.create_user(username='test', password='testpass',
                                             email='testadmin@example.com')
        self.client.login(username='test', password='testpass')
        new_project = Project.objects.create(name='testproject',
                                             creation_date=timezone.now(),
                                             work_start_date=timezone.now())
        self.page_url = '/project-report/{}/'.format(new_project.pk)

    def test_url_resolves_to_project_report_view(self):
        found = resolve(self.page_url)
        self.assertEqual(found.func.__name__, ProjectReportView.__name__)

    def test_page_responds_with_200(self):
        response = self.client.get(self.page_url)
        self.assertEqual(response.status_code, 200)

    def test_page_uses_correct_template(self):
        response = self.client.get(self.page_url)
        self.assertTemplateUsed(response, 'HuskyJamGuru/project_report.html')

    def test_project_report_renders_correctly(self):
        today = timezone.now().date()

        new_project = Project(name="test_project")
        new_project.work_start_date = today - datetime.timedelta(days=4)
        new_project.deadline_date = timezone.now().date()
        new_project.save()

        new_gitlab_project = GitlabProject(name="test_gitlab_project")
        new_gitlab_project.gitlab_id = 4
        new_gitlab_project.project = new_project
        new_gitlab_project.save()

        new_gitlab_issue = GitLabIssue(name="test_gilat_issue")
        new_gitlab_issue.gitlab_project = new_gitlab_project
        new_gitlab_issue.gitlab_issue_id = 5
        new_gitlab_issue.gitlab_issue_iid = 3
        new_gitlab_issue.save()

        new_gitlab_issue2 = GitLabIssue(name="test_gilat_issue2")
        new_gitlab_issue2.gitlab_project = new_gitlab_project
        new_gitlab_issue2.gitlab_issue_id = 6
        new_gitlab_issue2.gitlab_issue_iid = 4
        new_gitlab_issue2.save()

        new_gitlab_issue3 = GitLabIssue(name="test_gilat_issue3")
        new_gitlab_issue3.gitlab_project = new_gitlab_project
        new_gitlab_issue3.gitlab_issue_id = 7
        new_gitlab_issue3.gitlab_issue_iid = 5
        new_gitlab_issue3.save()

        new_gitlab_issue_type_update = IssueTypeUpdate()
        new_gitlab_issue_type_update.time = today - datetime.timedelta(days=3)
        new_gitlab_issue_type_update.gitlab_issue = new_gitlab_issue
        new_gitlab_issue_type_update.type = "verified"
        new_gitlab_issue_type_update.project = new_project
        new_gitlab_issue_type_update.save()

        new_gitlab_issue2_type_update = IssueTypeUpdate()
        new_gitlab_issue2_type_update.time = today - datetime.timedelta(days=1)
        new_gitlab_issue2_type_update.gitlab_issue = new_gitlab_issue2
        new_gitlab_issue2_type_update.type = "verified"
        new_gitlab_issue2_type_update.project = new_project
        new_gitlab_issue2_type_update.save()

        report_list = new_project.report_list

        assert_list = [{'date': today - datetime.timedelta(days=4), 'issues': 3},
                       {'date': today - datetime.timedelta(days=3), 'issues': 3},
                       {'date': today - datetime.timedelta(days=2), 'issues': 3},
                       {'date': today - datetime.timedelta(days=1), 'issues': 3},
                       {'date': today - datetime.timedelta(days=0), 'issues': 1}]

        self.assertEquals(report_list, assert_list)


class ProjectUpdateTest(TestCase):

    def get_inline_work_form_data(self):
        return {
            'work_time_evaluation-TOTAL_FORMS': 1,
            'work_time_evaluation-INITIAL_FORMS': 0,
            'work_time_evaluation-MIN_NUM_FORMS': 0,
            'work_time_evaluation-MAX_NUM_FORMS': 1000
        }

    def setUp(self):
        self.user = get_user_model().objects.create_superuser(username='test', password='testpass',
                                                              email='testadmin@example.com')
        GitlabAuthorisation.objects.create(user=self.user, gitlab_user_id=5, token='blablabla')
        self.client.login(username='test', password='testpass')
        mile, _, _ = create_data()
        new_project = mile.gitlab_project.project
        new_project.work_start_date = new_project.creation_date + datetime.timedelta(days=3)
        new_project.save()
        self.project = new_project
        self.page_url = '/project-update/{}/'.format(self.project.pk)

    def test_url_resolves_to_work_report_list_view(self):
        found = resolve(self.page_url)
        self.assertEqual(found.func.__name__, ProjectUpdateView.__name__)

    def test_page_responds_with_200(self):
        response = self.client.get(self.page_url)
        self.assertEqual(response.status_code, 200)

    def test_page_redirects_to_login_if_simple_user(self):
        user = get_user_model().objects.create_user(username='notsuper', password='testpass')
        GitlabAuthorisation.objects.create(user=user, gitlab_user_id=3, token='toke')
        self.client.login(username='notsuper', password='testpass')
        response = self.client.get(self.page_url)
        self.assertRedirects(response, '/login?next={}'.format(self.page_url))

    def test_page_not_redirects_if_manager(self):
        user = get_user_model().objects.create_user(username='usermanager', password='testpass')
        GitlabAuthorisation.objects.create(user=user, gitlab_user_id=3, token='toke')
        UserToProjectAccess.objects.create(user=user, project=self.project, type='manager')
        self.client.login(username='usermanager', password='testpass')
        response = self.client.get(self.page_url)
        self.assertEqual(response.status_code, 200)

    def test_page_uses_correct_template(self):
        response = self.client.get(self.page_url)
        self.assertTemplateUsed(response, 'HuskyJamGuru/project_update.html')

    def test_project_detail_contains_link_to_project_update(self):
        response = self.client.get('/project-detail/{}/'.format(self.project.pk))
        self.assertContains(response, self.page_url)

    def test_date_updates_after_post(self):
        new_date = self.project.work_start_date + datetime.timedelta(days=3)
        new_date_string = new_date.strftime('%Y-%m-%d')

        data = {
            'name': 'test_name',
            'status': 'presale',
            'issues_types': 'cool, nice, the best',
            'work_start_date': new_date_string
        }
        data.update(self.get_inline_work_form_data())

        self.client.post(self.page_url, data)

        project = Project.objects.get(pk=self.project.pk)
        self.assertEqual(project.work_start_date, new_date)

    def test_columns_saves_correctly(self):
        data = {
            'name': 'test_name',
            'status': 'presale',
            'issues_types': 'cool, nice, the best'
        }
        data.update(self.get_inline_work_form_data())

        self.client.post(self.page_url, data)
        project = Project.objects.get(pk=self.project.pk)

        self.assertEqual(project.issues_types, 'cool, nice, the best')

    def test_project_returns_correct_issues_types_tuple(self):

        data = {
            'name': 'test_name',
            'status': 'presale',
            'issues_types': 'cool, nice, the best',
        }
        data.update(self.get_inline_work_form_data())

        self.client.post(self.page_url, data)
        project = Project.objects.get(pk=self.project.pk)

        expected_tuple = (
            ('cool', 'Cool'),
            ('nice', 'Nice'),
            ('the_best', 'The Best'),
        )

        self.assertEqual(project.issues_types_tuple, expected_tuple)


class MilestoneSortTest(TestCase):
    def setUp(self):
        get_user_model().objects.create_superuser(username='test', password='testpass',
                                                  email='testadmin@example.com')
        self.client.login(username='test', password='testpass')

    def test_new_milestone_created_with_right_priority(self):
        mile1, mile2, mile3 = create_data()

        self.assertEqual(mile1.priority, 1)
        self.assertEqual(mile2.priority, 2)
        self.assertEqual(mile3.priority, 3)

    def test_milestones_sorts_correctly(self):
        mile1, mile2, mile3 = create_data()

        data = {
            'milestone_id': mile2.pk,
            'direction': 'up',
        }

        self.client.post('/sort-milestones', data)
        milestones = GitlabProject.objects.first().gitlab_milestones.all()

        self.assertEqual(milestones[0], mile2)
        self.assertEqual(milestones[1], mile1)
        self.assertEqual(milestones[2], mile3)

        data = {
            'milestone_id': mile1.pk,
            'direction': 'down',
        }
        self.client.post('/sort-milestones', data)

        milestones = GitlabProject.objects.first().gitlab_milestones.all()

        self.assertEqual(milestones[0], mile2)
        self.assertEqual(milestones[1], mile3)
        self.assertEqual(milestones[2], mile1)

    def test_ajax_sorting_works(self):
        mile1, mile2, mile3 = create_data()

        data = {
            'milestone_id': mile2.pk,
            'direction': 'up',
        }

        response = self.client.post('/sort-milestones', data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)

        milestones = GitlabProject.objects.first().gitlab_milestones.all()

        self.assertEqual(milestones[0], mile2)
        self.assertEqual(milestones[1], mile1)
        self.assertEqual(milestones[2], mile3)

    def test_only_superuser_can_sort_milestones(self):
        mile1, mile2, mile3 = create_data()

        get_user_model().objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        data = {
            'milestone_id': mile1.pk,
            'direction': 'down',
        }
        response = self.client.post('/sort-milestones', data)

        self.assertEqual(response.status_code, 403)


class TestLoginAsGuruUser(TestCase):
    def setUp(self):
        get_user_model().objects.create_superuser(username='test', password='testpass',
                                                  email='testadmin@example.com')

    def test_login_page_contains_link_to_login_as_guru(self):
        response = self.client.get(reverse('HuskyJamGuru:login'))
        self.assertContains(response, '/login-as-guru/')

    def test_url_resolves_to_work_report_list_view(self):
        found = resolve('/login-as-guru/')
        self.assertEqual(found.func.__name__, LoginAsGuruUserView.__name__)

    def test_page_responds_with_200(self):
        response = self.client.get('/login-as-guru/')
        self.assertEqual(response.status_code, 200)

    def test_page_uses_correct_template(self):
        response = self.client.get('/login-as-guru/')
        self.assertTemplateUsed(response, 'admin/login.html')

    def test_page_contains_auth_form(self):
        response = self.client.get('/login-as-guru/')
        self.assertIsInstance(response.context['form'], AuthenticationForm)

    def test_page_authenticates(self):
        data = {
            'username': 'test',
            'password': 'testpass'
        }

        response = self.client.post('/login-as-guru/', data, follow=True)
        self.assertEqual(response.context['user'].is_authenticated(), True)

    def test_page_redirects_to_project_list_after_auth(self):
        data = {
            'username': 'test',
            'password': 'testpass'
        }

        response = self.client.post('/login-as-guru/', data, follow=True)
        self.assertRedirects(response, reverse('HuskyJamGuru:project-list'))


class TestWorkPlans(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='test',
            password='testpass',
            email='testuser@example.com'
        )

        # Записываем разные планы на один день, последний должен перекрыть предыдущие
        PersonalDayWorkPlan(user=self.user, date=datetime.date(2015, 3, 11), work_hours=1).save()
        PersonalDayWorkPlan(user=self.user, date=datetime.date(2015, 3, 11), work_hours=3).save()
        PersonalDayWorkPlan(user=self.user, date=datetime.date(2015, 3, 11), work_hours=2).save()

        PersonalDayWorkPlan(user=self.user, date=datetime.date(2015, 5, 11), work_hours=4).save()
        PersonalDayWorkPlan(user=self.user, date=datetime.date(2015, 5, 12), work_hours=4).save()
        PersonalDayWorkPlan(user=self.user, date=datetime.date(2015, 5, 13), work_hours=4).save()

    def test_getting(self):
        work_plan = PersonalDayWorkPlan.get_work_plan(self.user, datetime.date(2015, 3, 9), datetime.date(2015, 3, 10))
        self.assertQuerysetEqual(work_plan, PersonalDayWorkPlan.objects.none())

        work_plan = PersonalDayWorkPlan.get_work_plan(self.user, datetime.date(2015, 3, 9), datetime.date(2015, 5, 10))
        self.assertEqual(len(work_plan), 1)

        work_plan = PersonalDayWorkPlan.get_work_plan(self.user, datetime.date(2015, 3, 9), datetime.date(2015, 5, 11))

        self.assertEqual(len(work_plan), 2)
        self.assertEqual(work_plan[0].work_hours, 2)
        self.assertEqual(work_plan[1].work_hours, 4)

    def test_getting_borders(self):
        days = PersonalDayWorkPlan.get_amount_of_unceasingly_planned_days(self.user, datetime.date(2015, 3, 11))
        self.assertEqual(days, 0)

        days = PersonalDayWorkPlan.get_amount_of_unceasingly_planned_days(self.user, datetime.date(2015, 5, 11))
        self.assertEqual(days, 2)


class PersonalTimeReportTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(username='test', password='testpass',
                                                              email='testadmin@example.com')
        self.client.login(username='test', password='testpass')

        self.report_user = get_user_model().objects.create_user(username='reportuser', password='report')
        mile, _, _ = create_data()
        new_project = mile.gitlab_project.project
        GitlabAuthorisation.objects.create(user=self.user, gitlab_user_id=5, token='blablabla')
        self.project = new_project
        self.page_url = '/personal-time-report/{}/'.format(self.report_user.pk)

    def test_url_resolves_to_right_view(self):
        found = resolve(self.page_url)
        self.assertEqual(found.func.__name__, PersonalTimeReportView.__name__)

    def test_page_responds_with_200(self):
        response = self.client.get(self.page_url)
        self.assertEqual(response.status_code, 200)

    def test_page_uses_correct_template(self):
        response = self.client.get(self.page_url)
        self.assertTemplateUsed(response, 'HuskyJamGuru/personal_time_report.html')

    def test_page_redirects_to_login_if_not_superuser(self):
        get_user_model().objects.create_user(username='notsuper', password='testpass')
        self.client.login(username='notsuper', password='testpass')
        response = self.client.get(self.page_url)
        self.assertRedirects(response, '/login?next={}'.format(self.page_url))

    def test_right_user_object_in_context(self):
        response = self.client.get(self.page_url)
        self.assertEqual(response.context['report_user'], self.report_user)

    def test_work_report_list_contains_link_to_personal_time_report(self):
        response = self.client.get('/work-report-list/')
        self.assertContains(response, self.page_url)

    def test_weekly_time_spent_records(self):
        mile = self.project.gitlab_projects.first().gitlab_milestones.first()
        issue = GitLabIssue.objects.create(gitlab_milestone=mile,
                                           gitlab_issue_id=5,
                                           gitlab_issue_iid=6,
                                           gitlab_project=self.project.gitlab_projects.first())
        record1 = IssueTimeSpentRecord.objects.create(
            user=self.user, gitlab_issue=issue,
            time_start=timezone.datetime(
                2015, 7, 8, tzinfo=timezone.get_current_timezone()
            )
        )
        record2 = IssueTimeSpentRecord.objects.create(
            user=self.user, gitlab_issue=issue,
            time_start=timezone.datetime(
                2015, 7, 10, tzinfo=timezone.get_current_timezone()
            )
        )
        record3 = IssueTimeSpentRecord.objects.create(
            user=self.user, gitlab_issue=issue,
            time_start=timezone.datetime(
                2015, 9, 22, tzinfo=timezone.get_current_timezone()
            )
        )
        record4 = IssueTimeSpentRecord.objects.create(
            user=self.user, gitlab_issue=issue,
            time_start=timezone.datetime(
                2015, 9, 24, tzinfo=timezone.get_current_timezone()
            )
        )
        record5 = IssueTimeSpentRecord.objects.create(
            user=self.user, gitlab_issue=issue,
            time_start=timezone.datetime(
                2015, 9, 26, tzinfo=timezone.get_current_timezone()
            )
        )

        week1 = {
            'start_date': datetime.date(2015, 7, 6),
            'end_date': datetime.date(2015, 7, 12),
            'records': [
                record1,
                record2,
            ]
        }
        week2 = {
            'start_date': datetime.date(2015, 9, 21),
            'end_date': datetime.date(2015, 9, 27),
            'records': [
                record3,
                record4,
                record5,
            ]
        }

        found_week1 = False
        found_week2 = False

        weekly_records = self.user.gitlabauthorisation.weekly_time_spent_records
        for week in weekly_records:
            if week['start_date'] == week1['start_date'] and week['end_date'] == week1['end_date']:
                found_week1 = True
                self.assertEqual(week['records'].count(), 2)
                for record in week1['records']:
                    self.assertIn(record, week['records'])
            elif week['start_date'] == week2['start_date'] and week['end_date'] == week2['end_date']:
                found_week2 = True
                self.assertEqual(week['records'].count(), 3)
                for record in week2['records']:
                    self.assertIn(record, week['records'])

        self.assertTrue(found_week1)
        self.assertTrue(found_week2)
