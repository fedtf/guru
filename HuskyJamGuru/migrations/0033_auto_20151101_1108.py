# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0032_personaldayworkplan_is_actual'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='finish_date_assessment',
        ),
        migrations.AddField(
            model_name='project',
            name='deadline_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
