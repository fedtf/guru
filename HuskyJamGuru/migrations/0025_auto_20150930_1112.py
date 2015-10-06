# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0024_gitlabproject_finish_date_assessment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gitlabproject',
            name='creation_date',
        ),
        migrations.RemoveField(
            model_name='gitlabproject',
            name='finish_date_assessment',
        ),
        migrations.AddField(
            model_name='project',
            name='creation_date',
            field=models.DateField(default=datetime.datetime(2015, 9, 30, 11, 12, 6, 777014, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='project',
            name='finish_date_assessment',
            field=models.DateField(default=datetime.datetime(2015, 9, 30, 11, 12, 50, 400454, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
