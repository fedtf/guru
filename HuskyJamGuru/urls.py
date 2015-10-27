from django.conf.urls import url, include
from Project import settings

from HuskyJamGuru.views import Login, ProjectListView, ProjectDetailView, IssueTimeAssessmentCreate,\
    synchronise_with_gitlab, WorkReportListView, ProjectReportView, SortMilestonesView,\
    LoginAsGuruUserView, ProjectUpdateView, PersonalTimeReportView, milestones_fix, UpdateItemFromGitlabView,\
    CheckIfTaskIsDoneView, telegram_webhook, set_webhook


urlpatterns = [
    url(r'^login$', Login.as_view(), name="login"),
    url(r'^login-as-guru/$', LoginAsGuruUserView.as_view(), name='login-as-guru'),
    url(r'^$', ProjectListView.as_view(), name='project-list'),
    url(r'^synchronise-with-gitlab/$', synchronise_with_gitlab, name='synchronise-with-gitlab'),
    url(r'^project-detail/(?P<pk>\d+)/$', ProjectDetailView.as_view(), name='project-detail'),
    url(r'^project-update/(?P<pk>\d+)/$', ProjectUpdateView.as_view(), name='project-update'),
    url(r'^project-report/(?P<pk>\d+)/$', ProjectReportView.as_view(), name='project-report'),
    url(r'^personal-time-report/(?P<pk>\d+)/$', PersonalTimeReportView.as_view(), name='personal-time-report'),
    url(r'^sort-milestones$', SortMilestonesView.as_view(), name='sort-milestones'),
    url(r'^milestones-fix/$', milestones_fix, name='milestones-fix'),
    url(r'^update-item-from-gitlab/$', UpdateItemFromGitlabView.as_view(), name='update-item-from-gitlab'),
    url(r'^check-if-task-is-done/$', CheckIfTaskIsDoneView.as_view(), name='check-if-task-is-done'),
    url(r'set-telegram-webhook/$', set_webhook, name='set-telegram-webhook'),
    url(r'^{}'.format(settings.TELEGRAM_BOT_TOKEN), telegram_webhook, name='telegram-webhook'),
    url(
        r'^issue-time-assessment-create/(?P<issue_pk>\d+)/$',
        IssueTimeAssessmentCreate.as_view(),
        name='issue-time-assessment-create'
    ),
    url(r'^work-report-list/$', WorkReportListView.as_view(), name='work-report-list'),
    url(r'^api/', include('HuskyJamGuru.urls_api')),
]
