from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^', include('HuskyJamGuru.urls', namespace='HuskyJamGuru')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': "HuskyJamGuru:login"}, name="logout"),
]
