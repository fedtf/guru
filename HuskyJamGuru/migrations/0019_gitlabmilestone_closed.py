# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0018_auto_20150916_1702'),
    ]

    operations = [
        migrations.AddField(
            model_name='gitlabmilestone',
            name='closed',
            field=models.BooleanField(default=False),
        ),
    ]
