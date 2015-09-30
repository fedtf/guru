import datetime

from django.test import TestCase
from django.core.urlresolvers import resolve
from django.contrib.auth import get_user_model
from django.utils import timezone

from .views import WorkReportListView, ProjectReportView
from .models import Project, IssueTypeUpdate, GitlabProject, GitLabIssue


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
        response = self.client.get('/work-report-list/', follow=True)
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
