from rest_framework import serializers

from .models import IssueTypeUpdate, GitLabIssue, IssueTimeSpentRecord, GitlabAuthorisation, Project


class IssueTimeSpentRecordSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        many=False, read_only=True,
    )

    gitlab_issue = serializers.PrimaryKeyRelatedField(
        many=False, read_only=True,
    )

    class Meta:
        model = IssueTimeSpentRecord
        fields = ('user', 'gitlab_issue', 'time_start', 'time_stop', 'seconds')


class IssueTypeUpdateSerializer(serializers.HyperlinkedModelSerializer):
    gitlab_issue = serializers.PrimaryKeyRelatedField(
        many=False, read_only=False, queryset=GitLabIssue.objects.all()
    )

    author = serializers.PrimaryKeyRelatedField(
        many=False, read_only=True,
    )

    project = serializers.PrimaryKeyRelatedField(
        many=False, read_only=False, queryset=Project.objects.all()
    )

    class Meta:
        model = IssueTypeUpdate
        fields = ('gitlab_issue', 'type', 'pk', 'author', 'project')


class GitlabAuthorisationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GitlabAuthorisation
        fields = ('name', )


class GitLabIssueSerializer(serializers.HyperlinkedModelSerializer):

    gitlab_milestone = serializers.PrimaryKeyRelatedField(
        many=False, read_only=True,
    )

    assignee = GitlabAuthorisationSerializer()

    current_type = IssueTypeUpdateSerializer()

    class Meta:
        model = GitLabIssue
        fields = (
            'name',
            'description',
            'pk',
            'current_type',
            'gitlab_milestone',
            'spent_minutes',
            'link',
            'assignee',
            'gitlab_issue_id'
        )
