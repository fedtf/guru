# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0013_issuetypeupdate_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='gitlabproject',
            name='namespace',
            field=models.CharField(blank=True, max_length=500),
        ),
    ]
