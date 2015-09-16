# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0012_issuetypeupdate_author'),
    ]

    operations = [
        migrations.AddField(
            model_name='issuetypeupdate',
            name='time',
            field=models.DateTimeField(default=datetime.datetime.now(), auto_now=True),
            preserve_default=False,
        ),
    ]
