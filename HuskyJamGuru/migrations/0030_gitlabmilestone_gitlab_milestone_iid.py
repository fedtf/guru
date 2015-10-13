# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0029_auto_20151007_1000'),
    ]

    operations = [
        migrations.AddField(
            model_name='gitlabmilestone',
            name='gitlab_milestone_iid',
            field=models.IntegerField(default=1, blank=None),
            preserve_default=False,
        ),
    ]
