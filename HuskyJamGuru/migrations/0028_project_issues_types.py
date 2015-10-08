# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0027_auto_20150930_1839'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='issues_types',
            field=models.TextField(default='open, in progress, fixed, verified'),
        ),
    ]
