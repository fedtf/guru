# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0036_auto_20151101_1247'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='status',
            field=models.CharField(max_length=100, choices=[('presale', 'Presale'), ('in-development', 'In development'), ('finished', 'Finished')], default='in-development'),
            preserve_default=False,
        ),
    ]
