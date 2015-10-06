# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0021_auto_20150929_0831'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gitlabproject',
            name='creation_time',
            field=models.DateField(),
        ),
    ]
