# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0031_telegramuser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='telegramuser',
            name='user',
            field=models.OneToOneField(related_name='telegram_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
