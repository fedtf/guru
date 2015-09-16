# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0002_gitlabissue_gitlab_milestone_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gitlabissue',
            name='gitlab_milestone_id',
        ),
        migrations.AddField(
            model_name='gitlabissue',
            name='gitlab_milestone',
            field=models.ForeignKey(blank=True, to='HuskyJamGuru.GitLabMilestone', null=True),
        ),
    ]
