# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GitlabAuthorisation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('gitlab_user_id', models.IntegerField(unique=True, blank=None)),
                ('token', models.CharField(max_length=500)),
                ('name', models.CharField(max_length=500, blank=True)),
                ('username', models.CharField(max_length=500, blank=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='GitLabIssue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('gitlab_issue_id', models.IntegerField(blank=None)),
                ('name', models.CharField(max_length=500, blank=True)),
                ('description', models.CharField(max_length=1000, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='GitLabMilestone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('gitlab_milestone_id', models.IntegerField(blank=None)),
                ('name', models.CharField(max_length=500, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='GitlabModelExtension',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('gitlab_id', models.IntegerField(unique=True, blank=None)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='UserToProjectAccess',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=100)),
                ('project', models.ForeignKey(related_name='user_project_accesses', to='HuskyJamGuru.Project')),
                ('user', models.ForeignKey(related_name='to_project_accesses', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='GitLabBuild',
            fields=[
                ('gitlabmodelextension_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='HuskyJamGuru.GitlabModelExtension')),
                ('test_link', models.CharField(max_length=500, null=True, blank=True)),
                ('time', models.DateTimeField()),
                ('author', models.ForeignKey(related_name='gitlab_builds', to='HuskyJamGuru.GitlabAuthorisation')),
            ],
            bases=('HuskyJamGuru.gitlabmodelextension',),
        ),
        migrations.CreateModel(
            name='GitLabMR',
            fields=[
                ('gitlabmodelextension_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='HuskyJamGuru.GitlabModelExtension')),
                ('name', models.CharField(max_length=500, blank=True)),
                ('milestone', models.ForeignKey(blank=True, to='HuskyJamGuru.GitLabMilestone', null=True)),
            ],
            bases=('HuskyJamGuru.gitlabmodelextension',),
        ),
        migrations.CreateModel(
            name='GitlabProject',
            fields=[
                ('gitlabmodelextension_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='HuskyJamGuru.GitlabModelExtension')),
                ('name', models.CharField(max_length=500, blank=True)),
                ('name_with_namespace', models.CharField(max_length=500, blank=True)),
                ('project', models.ForeignKey(related_name='gitlab_projects', blank=True, to='HuskyJamGuru.Project', null=True)),
            ],
            bases=('HuskyJamGuru.gitlabmodelextension',),
        ),
        migrations.AddField(
            model_name='gitlabmilestone',
            name='gitlab_project',
            field=models.ForeignKey(to='HuskyJamGuru.GitlabProject', blank=None),
        ),
        migrations.AddField(
            model_name='gitlabissue',
            name='gitlab_project',
            field=models.ForeignKey(to='HuskyJamGuru.GitlabProject', blank=None),
        ),
        migrations.AddField(
            model_name='gitlabbuild',
            name='gitlab_mr',
            field=models.ForeignKey(related_name='gitlab_builds', to='HuskyJamGuru.GitLabMilestone'),
        ),
    ]
