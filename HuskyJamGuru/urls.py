from django.conf.urls import url

from HuskyJamGuru.views import *

urlpatterns = [
    url(r'^$', Dashboard.as_view(), name="dashboard"),
    url(r'^login$', Login.as_view(), name="login"),
]
