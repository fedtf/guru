# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('HuskyJamGuru', '0010_auto_20150913_1813'),
    ]

    operations = [
        migrations.CreateModel(
            name='IssueTimeSpentRecord',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('time_start', models.DateTimeField()),
                ('time_stop', models.DateTimeField(null=True, blank=True)),
                ('gitlab_issue', models.ForeignKey(related_name='time_spent_records', to='HuskyJamGuru.GitLabIssue')),
                ('user', models.ForeignKey(related_name='issues_time_spent_records', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='IssueTypeUpdate',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('type', models.CharField(max_length=100)),
                ('gitlab_issue', models.ForeignKey(related_name='type_update', to='HuskyJamGuru.GitLabIssue')),
            ],
        ),
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(default='', max_length=500),
        ),
    ]
