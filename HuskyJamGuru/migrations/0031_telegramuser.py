# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import multiselectfield.db.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('HuskyJamGuru', '0030_gitlabmilestone_gitlab_milestone_iid'),
    ]

    operations = [
        migrations.CreateModel(
            name='TelegramUser',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('notification_events', multiselectfield.db.fields.MultiSelectField(max_length=29, choices=[('issue', 'New Issue Comments'), ('milestone', 'New Milestone Comments'), ('merge_request', 'New Merge Requests')])),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
