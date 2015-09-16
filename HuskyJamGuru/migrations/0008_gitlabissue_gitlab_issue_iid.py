# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0007_auto_20150913_1738'),
    ]

    operations = [
        migrations.AddField(
            model_name='gitlabissue',
            name='gitlab_issue_iid',
            field=models.IntegerField(default=1, blank=None),
            preserve_default=False,
        ),
    ]
