# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0005_auto_20150912_1839'),
    ]

    operations = [
        migrations.AddField(
            model_name='gitlabproject',
            name='name',
            field=models.CharField(max_length=500, blank=True),
        ),
        migrations.AddField(
            model_name='gitlabproject',
            name='name_with_namespace',
            field=models.CharField(max_length=500, blank=True),
        ),
    ]
