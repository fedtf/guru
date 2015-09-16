# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0005_auto_20150913_1727'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gitlabissue',
            name='updated_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
