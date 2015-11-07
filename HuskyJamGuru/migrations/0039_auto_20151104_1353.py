# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0038_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='gitlabmilestone',
            name='rolled_up',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='project',
            name='status',
            field=models.CharField(max_length=100, choices=[('presale', 'Presale'), ('in-development', 'In development'), ('finished', 'Finished')], default=('presale', 'Presale')),
        ),
    ]
