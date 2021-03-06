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

    def create(self, request, *args, **kwargs):
        issue = GitLabIssue.objects.get(pk=request.data['gitlab_issue'])
        if issue.current_type.type != 'in_progress' and request.data['type'] == 'in_progress':
            issue.assignee = request.user.gitlabauthorisation
            issue.save()
            for type_update in IssueTypeUpdate.objects.filter(
                    author=request.user, type='in_progress', is_current=True
            ).all():
                if type_update.gitlab_issue != issue:
                    new_update = IssueTypeUpdate(
                        gitlab_issue=type_update.gitlab_issue,
                        type='open',
                        author=request.user,
                        project_id=type_update.gitlab_issue.gitlab_project.project
                    )
                    new_update.save()
            issue.reassign_to_user(request.user)
        if request.data['type'] == 'verified':
            issue.change_state_in_gitlab('close')
        elif issue.current_type.type == 'verified':
            issue.change_state_in_gitlab('reopen')
        request.POST._mutable = True
        request.data['project'] = issue.gitlab_project.project.pk
        request.POST._mutable = False
        return super(self.__class__, self).create(request, *args, **kwargs)


class GitLabIssueViewSet(viewsets.ModelViewSet):
    serializer_class = GitLabIssueSerializer

    def get_queryset(self):
        if 'project_pk' in self.request.query_params:
            return GitLabIssue.objects.filter(gitlab_project__project=self.request.query_params['project_pk']).all()
        elif 'milestone_pk' in self.request.query_params:
            return GitLabIssue.objects.filter(gitlab_milestone=self.request.query_params['milestone_pk']).all()
        elif 'issue_pk' in self.request.query_params:
            return GitLabIssue.objects.get(pk=self.request.query_params['issue_pk'])
        return GitLabIssue.objects.all()


class IssueTimeSpentRecordViewSet(viewsets.ModelViewSet):
    serializer_class = IssueTimeSpentRecordSerializer
    queryset = IssueTimeSpentRecord.objects.all()
