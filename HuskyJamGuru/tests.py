import datetime

from django.test import TestCase
from django.core.urlresolvers import resolve, reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.auth.forms import AuthenticationForm

from .views import WorkReportListView, ProjectReportView, ProjectColumnsEditView, LoginAsGuruUserView
from .models import Project, IssueTypeUpdate, GitlabProject, GitLabIssue, GitLabMilestone,\
    UserToProjectAccess


def create_data():
    project = Project(name='testproject', creation_date=timezone.now(),
                      finish_date_assessment=timezone.now())
    project.save()

    gitlab_project = GitlabProject(name='gitlabtestproject', gitlab_id=4,
                                   project=project)
    gitlab_project.save()

    mile1 = GitLabMilestone(name='mile1', gitlab_project=gitlab_project,
                            gitlab_milestone_id=1)
    mile1.save()

    mile2 = GitLabMilestone(name='mile2', gitlab_project=gitlab_project,
                            gitlab_milestone_id=2)
    mile2.save()

    mile3 = GitLabMilestone(name='mile3', gitlab_project=gitlab_project,
                            gitlab_milestone_id=3)
    mile3.save()

    return (mile1, mile2, mile3)


class WorkReportListTest(TestCase):
    def setUp(self):
        get_user_model().objects.create_superuser(username='test', password='testpass',
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


class ProjectReportTest(TestCase):
    def setUp(self):
        get_user_model().objects.create_user(username='test', password='testpass',
                                             email='testadmin@example.com')
        self.client.login(username='test', password='testpass')
        new_project = Project.objects.create(name='testproject',
                                             creation_date=timezone.now(),
                                             finish_date_assessment=timezone.now())
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
        new_project.creation_date = today - datetime.timedelta(days=4)
        new_project.finish_date_assessment = timezone.now().date()
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
        new_gitlab_issue_type_update.type = "closed"
        new_gitlab_issue_type_update.project = new_project
        new_gitlab_issue_type_update.save()

        new_gitlab_issue2_type_update = IssueTypeUpdate()
        new_gitlab_issue2_type_update.time = today - datetime.timedelta(days=1)
        new_gitlab_issue2_type_update.gitlab_issue = new_gitlab_issue2
        new_gitlab_issue2_type_update.type = "closed"
        new_gitlab_issue2_type_update.project = new_project
        new_gitlab_issue2_type_update.save()

        report_list = new_project.report_list

        assert_list = [{'date': today - datetime.timedelta(days=4), 'issues': 3},
                       {'date': today - datetime.timedelta(days=3), 'issues': 3},
                       {'date': today - datetime.timedelta(days=2), 'issues': 3},
                       {'date': today - datetime.timedelta(days=1), 'issues': 3},
                       {'date': today - datetime.timedelta(days=0), 'issues': 1}]

        self.assertEquals(report_list, assert_list)


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


class ProjectColumnsEditTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(username='test', password='testpass',
                                                              email='testadmin@example.com')
        self.client.login(username='test', password='testpass')

        mile, _, _ = create_data()
        new_project = mile.gitlab_project.project
        self.project = new_project
        self.page_url = '/project-columns-edit/{}/'.format(new_project.pk)

    def test_url_resolves_to_work_report_list_view(self):
        found = resolve(self.page_url)
        self.assertEqual(found.func.__name__, ProjectColumnsEditView.__name__)

    def test_page_responds_with_200(self):
        response = self.client.get(self.page_url)
        self.assertEqual(response.status_code, 200)

    def test_page_redirects_to_login_if_not_superuser(self):
        get_user_model().objects.create_user(username='notsuper', password='testpass')
        self.client.login(username='notsuper', password='testpass')
        response = self.client.get(self.page_url)
        self.assertRedirects(response, '/login?next={}'.format(self.page_url))

    def test_page_uses_correct_template(self):
        response = self.client.get(self.page_url)
        self.assertTemplateUsed(response, 'HuskyJamGuru/project_columns_edit.html')

    def test_columns_saves_correctly(self):
        data = {
            'issues_types': 'cool, nice, the best'
        }

        self.client.post(self.page_url, data)
        project = Project.objects.get(pk=self.project.pk)

        self.assertEqual(project.issues_types, 'cool, nice, the best')

    def test_project_returns_correct_issues_types_tuple(self):
        data = {
            'issues_types': 'cool, nice, the best'
        }

        self.client.post(self.page_url, data)
        project = Project.objects.get(pk=self.project.pk)

        expected_tuple = (
            ('cool', 'Cool'),
            ('nice', 'Nice'),
            ('the_best', 'The Best'),
        )

        self.assertEqual(project.issues_types_tuple, expected_tuple)

    def test_detail_project_view_shows_unassigned_column_when_necessary(self):
        UserToProjectAccess.objects.create(user=self.user, project=self.project, type='developer')

        GitLabIssue.objects.create(gitlab_issue_id=0,
                                   gitlab_project=self.project.gitlab_projects.first(),
                                   gitlab_issue_iid=0)
        new_issue1 = GitLabIssue.objects.create(gitlab_issue_id=1,
                                                gitlab_project=self.project.gitlab_projects.first(),
                                                gitlab_issue_iid=1)
        IssueTypeUpdate.objects.create(gitlab_issue=new_issue1,
                                       project=self.project,
                                       type='in_progress')

        response = self.client.get('/project-detail/{}/'.format(self.project.pk))
        self.assertEqual(response.context['show_unassigned'], False)

        new_issue2 = GitLabIssue.objects.create(gitlab_issue_id=2,
                                                gitlab_project=self.project.gitlab_projects.first(),
                                                gitlab_issue_iid=2)
        IssueTypeUpdate.objects.create(gitlab_issue=new_issue2,
                                       project=self.project,
                                       type='unknown')

        response = self.client.get('/project-detail/{}/'.format(self.project.pk))
        self.assertEqual(response.context['show_unassigned'], True)


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
        self.assertTemplateUsed(response, 'HuskyJamGuru/login_as_guru.html')

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
