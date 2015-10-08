# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0028_project_issues_types'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issuetypeupdate',
            name='project',
            field=models.ForeignKey(related_name='issues_type_updates', editable=False, to='HuskyJamGuru.Project'),
        ),
    ]
