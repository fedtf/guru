# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='gitlabauthorisation',
            name='name',
            field=models.CharField(max_length=500, blank=True),
        ),
        migrations.AlterField(
            model_name='gitlabauthorisation',
            name='username',
            field=models.CharField(max_length=500, blank=True),
        ),
    ]
