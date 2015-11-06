# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0032_auto_20151027_1100'),
    ]

    operations = [
        migrations.AddField(
            model_name='telegramuser',
            name='telegram_id',
            field=models.CharField(max_length=50, blank=True),
        ),
        migrations.AlterField(
            model_name='telegramuser',
            name='notification_events',
            field=multiselectfield.db.fields.MultiSelectField(max_length=29, choices=[('issue', 'New Issue Comments'), ('milestone', 'New Milestone Comments'), ('merge_request', 'New Merge Requests')], blank=True),
        ),
    ]
