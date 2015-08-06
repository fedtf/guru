from django.conf.urls import include, url
from django.contrib import admin

from Project.gitlab import login_redirect, gitlab_auth_callback

urlpatterns = [
    url(r'^', include('HuskyJamGuru.urls', namespace='HuskyJamGuru')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^login_redirect$', login_redirect, name="gitlab_login_redirect"),
    url(r'^gitlab_auth_callback$', gitlab_auth_callback, name='gitlab_auth_callback'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': "HuskyJamGuru:login"}, name="logout"),
]
