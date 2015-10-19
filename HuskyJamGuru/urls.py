from django.conf.urls import url, include

from HuskyJamGuru.views import Login, ProjectListView, ProjectDetailView, IssueTimeAssessmentCreate,\
    synchronise_with_gitlab, WorkReportListView, ProjectReportView, SortMilestonesView,\
    LoginAsGuruUserView, ProjectUpdateView, milestones_fix


urlpatterns = [
    url(r'^login$', Login.as_view(), name="login"),
    url(r'^login-as-guru/$', LoginAsGuruUserView.as_view(), name='login-as-guru'),
    url(r'^$', ProjectListView.as_view(), name='project-list'),
    url(r'^synchronise-with-gitlab/$', synchronise_with_gitlab, name='synchronise-with-gitlab'),
    url(r'^project-detail/(?P<pk>\d+)/$', ProjectDetailView.as_view(), name='project-detail'),
    url(r'^project-update/(?P<pk>\d+)/$', ProjectUpdateView.as_view(), name='project-update'),
    url(r'^project-report/(?P<pk>\d+)/$', ProjectReportView.as_view(), name='project-report'),
    url(r'^sort-milestones$', SortMilestonesView.as_view(), name='sort-milestones'),
    url(r'^milestones-fix/$', milestones_fix, name='milestones-fix'),
    url(
        r'^issue-time-assessment-create/(?P<issue_pk>\d+)/$',
        IssueTimeAssessmentCreate.as_view(),
        name='issue-time-assessment-create'
    ),
    url(r'^work-report-list/$', WorkReportListView.as_view(), name='work-report-list'),
    url(r'^api/', include('HuskyJamGuru.urls_api')),
]
