from django.test import TestCase
from django.core.urlresolvers import resolve
from django.contrib.auth import get_user_model

from .views import WorkReportListView


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
