from django.conf.urls import url
from HuskyJamGuru.views import *

urlpatterns = [
    # url(r'^companies/$', Companies.as_view(), name="companies"),
    url(r'^$', Dashboard.as_view(), name="dashboard"),
    url(r'^$', Login.as_view(), name="login"),
    url(r'^$', Logout.as_view(), name="logout"),
]
