# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0020_auto_20150928_1402'),
    ]

    operations = [
        migrations.AddField(
            model_name='gitlabproject',
            name='creation_time',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 29, 8, 31, 46, 712382, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='issuetypeupdate',
            name='gitlab_issue',
            field=models.ForeignKey(related_name='type_updates', to='HuskyJamGuru.GitLabIssue'),
        ),
        migrations.AlterField(
            model_name='usertoprojectaccess',
            name='type',
            field=models.CharField(max_length=100, choices=[('administrator', 'Administrator'), ('developer', 'Developer'), ('manager', 'Manager')]),
        ),
    ]
