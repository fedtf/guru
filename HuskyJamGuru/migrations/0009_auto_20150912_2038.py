# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0008_auto_20150912_2031'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usertoprojectaccess',
            name='user',
            field=models.ForeignKey(related_name='to_project_accesses', to=settings.AUTH_USER_MODEL),
        ),
    ]
