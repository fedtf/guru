# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0014_gitlabproject_namespace'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gitlabproject',
            old_name='namespace',
            new_name='path_with_namespace',
        ),
    ]
