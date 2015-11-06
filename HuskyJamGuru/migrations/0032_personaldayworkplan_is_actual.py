# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0031_personaldayworkplan'),
    ]

    operations = [
        migrations.AddField(
            model_name='personaldayworkplan',
            name='is_actual',
            field=models.BooleanField(default=True),
        ),
    ]
