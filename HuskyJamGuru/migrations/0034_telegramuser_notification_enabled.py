# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0033_auto_20151027_1809'),
    ]

    operations = [
        migrations.AddField(
            model_name='telegramuser',
            name='notification_enabled',
            field=models.BooleanField(default=False),
        ),
    ]
