# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0022_auto_20150929_1026'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gitlabproject',
            old_name='creation_time',
            new_name='creation_date',
        ),
    ]
