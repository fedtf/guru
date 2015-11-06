# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0034_telegramuser_notification_enabled'),
    ]

    operations = [
        migrations.AlterField(
            model_name='telegramuser',
            name='notification_events',
            field=multiselectfield.db.fields.MultiSelectField(max_length=34, blank=True, choices=[('issue_create', 'Issue Opening'), ('issue_close', 'Issue Closing'), ('note', 'New Comments'), ('push', 'Push Events')]),
        ),
    ]
