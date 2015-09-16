# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0015_auto_20150916_1040'),
    ]

    operations = [
        migrations.AddField(
            model_name='gitlabissue',
            name='assignee',
            field=models.ForeignKey(null=True, blank=True, to='HuskyJamGuru.GitlabAuthorisation'),
        ),
    ]
