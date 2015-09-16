# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0006_auto_20150913_1732'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gitlabissue',
            name='gitlab_project',
            field=models.ForeignKey(related_name='issues', blank=None, to='HuskyJamGuru.GitlabProject'),
        ),
    ]
