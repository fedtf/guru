from django.conf.urls import url

from HuskyJamGuru.views import Login, ProjectListView, ProjectDetailView, IssueTimeAssessmentCreate

urlpatterns = [
    url(r'^login$', Login.as_view(), name="login"),

    url(r'^$', ProjectListView.as_view(), name='project-list'),
    url(r'^project-detail/(?P<pk>\d+)/$', ProjectDetailView.as_view(), name='project-detail'),
    url(r'^issue-time-assessment-create/(?P<issue_pk>\d+)/$', IssueTimeAssessmentCreate.as_view(), name='issue-time-assessment-create'),
]
