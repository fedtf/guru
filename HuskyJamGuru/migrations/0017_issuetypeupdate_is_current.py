# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0016_gitlabissue_assignee'),
    ]

    operations = [
        migrations.AddField(
            model_name='issuetypeupdate',
            name='is_current',
            field=models.BooleanField(default=True),
        ),
    ]
