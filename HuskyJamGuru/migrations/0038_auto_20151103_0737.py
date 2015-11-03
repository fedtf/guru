# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0037_project_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issuetimespentrecord',
            name='time_stop',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2015, 11, 3, 7, 37, 37, 773537, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='project',
            name='status',
            field=models.CharField(default=('presale', 'Presale'), choices=[('presale', 'Presale'), ('in-development', 'In development'), ('finished', 'Finished')], max_length=100),
        ),
        migrations.AlterField(
            model_name='worktimeevaluation',
            name='type',
            field=models.CharField(choices=[('markup', 'Markup'), ('backend', 'Backend'), ('testing', 'Testing'), ('ux', 'UX'), ('business-analyse', 'Business Analyse'), ('design', 'Design'), ('management', 'Management')], max_length=100),
        ),
    ]
