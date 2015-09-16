# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('HuskyJamGuru', '0008_gitlabissue_gitlab_issue_iid'),
    ]

    operations = [
        migrations.CreateModel(
            name='IssueAssessment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('minutes', models.IntegerField()),
                ('gitlab_issue', models.ForeignKey(related_name='assessments', to='HuskyJamGuru.GitLabIssue')),
                ('user', models.ForeignKey(related_name='issues_assessments', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
