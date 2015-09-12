# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0006_auto_20150912_2020'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gitlabproject',
            name='project',
            field=models.ForeignKey(related_name='gitlab_projects', blank=True, to='HuskyJamGuru.Project', null=True),
        ),
    ]
