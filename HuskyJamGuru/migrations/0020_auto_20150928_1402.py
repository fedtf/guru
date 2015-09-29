# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0019_gitlabmilestone_closed'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='issuetimespentrecord',
            options={'ordering': ['-time_start']},
        ),
    ]
