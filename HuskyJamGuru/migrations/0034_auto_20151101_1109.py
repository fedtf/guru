# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0033_auto_20151101_1108'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='work_start_date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='creation_date',
            field=models.DateField(auto_now=True),
        ),
    ]
