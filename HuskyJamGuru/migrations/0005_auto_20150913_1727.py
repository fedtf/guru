# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0004_gitlabissue_updated_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gitlabmilestone',
            name='gitlab_project',
            field=models.ForeignKey(related_name='gitlab_milestones', blank=None, to='HuskyJamGuru.GitlabProject'),
        ),
    ]
