# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0017_issuetypeupdate_is_current'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issuetypeupdate',
            name='author',
            field=models.ForeignKey(null=True, blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
