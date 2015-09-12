from django.conf.urls import url

from HuskyJamGuru.views import Dashboard, Login, ProjectListView, ProjectDetailView

urlpatterns = [
    url(r'^$', Dashboard.as_view(), name="dashboard"),
    url(r'^login$', Login.as_view(), name="login"),

    url(r'^project-list', ProjectListView.as_view(), name='project-create'),
    url(r'^project-detail/(?P<pk>\d+)/$', ProjectDetailView.as_view(), name='project-detail'),
]
