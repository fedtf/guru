# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import multiselectfield.db.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('HuskyJamGuru', '0040_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='PersonalNotification',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('telegram_id', models.CharField(max_length=50, blank=True)),
                ('telegram_notification_events', multiselectfield.db.fields.MultiSelectField(max_length=34, blank=True, choices=[('issue_create', 'Issue Opening'), ('issue_close', 'Issue Closing'), ('note', 'New Comments'), ('push', 'Push Events')])),
                ('email_notification_events', multiselectfield.db.fields.MultiSelectField(max_length=34, blank=True, choices=[('issue_create', 'Issue Opening'), ('issue_close', 'Issue Closing'), ('note', 'New Comments'), ('push', 'Push Events')])),
                ('enabled', models.BooleanField(default=False)),
                ('user', models.OneToOneField(related_name='notification', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='telegramuser',
            name='user',
        ),
        migrations.DeleteModel(
            name='TelegramUser',
        ),
    ]
