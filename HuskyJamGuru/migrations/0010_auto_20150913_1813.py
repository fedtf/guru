# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('HuskyJamGuru', '0009_issueassessment'),
    ]

    operations = [
        migrations.CreateModel(
            name='IssueTimeAssessment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('minutes', models.IntegerField()),
                ('gitlab_issue', models.ForeignKey(related_name='assessments', to='HuskyJamGuru.GitLabIssue')),
                ('user', models.ForeignKey(related_name='issues_assessments', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='issueassessment',
            name='gitlab_issue',
        ),
        migrations.RemoveField(
            model_name='issueassessment',
            name='user',
        ),
        migrations.DeleteModel(
            name='IssueAssessment',
        ),
    ]
