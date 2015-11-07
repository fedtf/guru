# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0012_issuetypeupdate_author'),
    ]

    operations = [
        migrations.AddField(
            model_name='issuetypeupdate',
            name='time',
            field=models.DateTimeField(default=timezone.now(), auto_now=True),
            preserve_default=False,
        ),
    ]
