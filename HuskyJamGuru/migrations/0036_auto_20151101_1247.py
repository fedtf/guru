# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0035_worktimeevaluation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='worktimeevaluation',
            name='project',
            field=models.ForeignKey(to='HuskyJamGuru.Project', related_name='work_time_evaluation'),
        ),
    ]
