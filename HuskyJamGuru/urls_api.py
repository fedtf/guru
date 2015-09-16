from django.conf.urls import url, include
from rest_framework import routers

from .views_api import IssueTypeUpdateViewSet, GitLabIssueViewSet, IssueTimeSpentRecordViewSet

router = routers.DefaultRouter()
router.register(r'IssueTypeUpdate', IssueTypeUpdateViewSet, base_name='issue-type-update')
router.register(r'GitLabIssue', GitLabIssueViewSet, base_name='gitlab-issue')
router.register(r'IssueTimeSpentRecord', IssueTimeSpentRecordViewSet)

urlpatterns = [
    url(r'^v1/', include(router.urls)),
]
