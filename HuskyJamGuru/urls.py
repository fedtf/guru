from django.conf.urls import url
from HuskyJamGuru.views import *

urlpatterns = [
    url(r'^$', Dashboard.as_view(), name="dashboard"),
    url(r'^login_redirect$', login_redirect, name="login_redirect"),
    url(r'^login$', Login.as_view(), name="login"),
    url(r'^gitlab_auth_redirect$', gitlab_auth_redirect, name='gitlab_auth_redirect'),
]

