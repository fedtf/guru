from rest_framework import viewsets

from .serializers import IssueTypeUpdateSerializer, GitLabIssueSerializer, IssueTimeSpentRecordSerializer
from .models import IssueTypeUpdate, GitLabIssue, IssueTimeSpentRecord


class IssueTypeUpdateViewSet(viewsets.ModelViewSet):
    serializer_class = IssueTypeUpdateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        if 'req_type' in self.request.query_params:
            if self.request.query_params['req_type'] == 'issue_current_type':
                return IssueTypeUpdate.objects.filter(
                    gitlab_issue=self.request.query_params['issue_pk']
                ).order_by('-pk')[0:1].all()

        return IssueTypeUpdate.objects.all()


class GitLabIssueViewSet(viewsets.ModelViewSet):
    serializer_class = GitLabIssueSerializer

    def get_queryset(self):
        if 'project_pk' in self.request.query_params:
                return GitLabIssue.objects.filter(gitlab_project__project=self.request.query_params['project_pk']).all()
        return GitLabIssue.objects.all()


class IssueTimeSpentRecordViewSet(viewsets.ModelViewSet):
    serializer_class = IssueTimeSpentRecordSerializer
    queryset = IssueTimeSpentRecord.objects.all()
