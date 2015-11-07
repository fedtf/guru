from django.conf.urls import url, include
from django.views.decorators.cache import cache_page

from HuskyJamGuru.views import Login, ProjectListView, ProjectDetailView, IssueTimeAssessmentCreate,\
    synchronise_with_gitlab, WorkReportListView, ProjectReportView, SortMilestoneView,\
    LoginAsGuruUserView, ProjectUpdateView, PersonalTimeReportView, milestones_fix, UpdateItemFromGitlabView,\
    CheckIfTaskIsDoneView, UserProfileView, GitlabWebhookView, PersonalPlanUpdateView,\
    ResourceManagementView, ChangeUserNotificationStateView, RollMilestoneView


urlpatterns = [
    url(r'^login$', Login.as_view(), name="login"),
    url(r'^login-as-guru/$', LoginAsGuruUserView.as_view(), name='login-as-guru'),
    url(r'^$', ProjectListView.as_view(), name='project-list'),
    url(r'^synchronise-with-gitlab/$', synchronise_with_gitlab, name='synchronise-with-gitlab'),
    url(r'^project-detail/(?P<pk>\d+)/$', ProjectDetailView.as_view(), name='project-detail'),
    url(r'^resource-management/$', cache_page(60)(ResourceManagementView.as_view()), name='resource-management'),
    url(r'^personal-plan/$', PersonalPlanUpdateView.as_view(), name='personal-plan'),
    url(r'^project-update/(?P<pk>\d+)/$', ProjectUpdateView.as_view(), name='project-update'),
    url(r'^project-report/(?P<pk>\d+)/$', ProjectReportView.as_view(), name='project-report'),
    url(r'^personal-time-report/(?P<pk>\d+)/$', PersonalTimeReportView.as_view(), name='personal-time-report'),
    url(r'^user-profile/(?P<pk>\d+)/$', UserProfileView.as_view(), name='user-profile'),
    url(r'^sort-milestone/(?P<pk>\d+)$', SortMilestoneView.as_view(), name='sort-milestone'),
    url(r'^roll-milestone/(?P<pk>\d+)$', RollMilestoneView.as_view(), name='roll-milestone'),
    url(r'^milestones-fix/$', milestones_fix, name='milestones-fix'),
    url(r'^update-item-from-gitlab/$', UpdateItemFromGitlabView.as_view(), name='update-item-from-gitlab'),
    url(r'^check-if-task-is-done/$', CheckIfTaskIsDoneView.as_view(), name='check-if-task-is-done'),
    url(
        r'^change-user-notification-state/(?P<user_pk>\d+)$',
        ChangeUserNotificationStateView.as_view(),
        name='change-user-notification-state'
    ),
    url(r'^gitlab-webhook', GitlabWebhookView.as_view(), name='gitlab_webhook'),
    url(
        r'^issue-time-assessment-create/(?P<issue_pk>\d+)/$',
        IssueTimeAssessmentCreate.as_view(),
        name='issue-time-assessment-create'
    ),
    url(r'^work-report-list/$', WorkReportListView.as_view(), name='work-report-list'),
    url(r'^api/', include('HuskyJamGuru.urls_api')),
]
