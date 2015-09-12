# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('HuskyJamGuru', '0007_auto_20150912_2021'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserToProjectAccess',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=100)),
                ('project', models.ForeignKey(related_name='user_project_accesses', to='HuskyJamGuru.Project')),
                ('user', models.ForeignKey(related_name='notifications_settings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='userprojectaccess',
            name='project',
        ),
        migrations.RemoveField(
            model_name='userprojectaccess',
            name='user',
        ),
        migrations.DeleteModel(
            name='UserProjectAccess',
        ),
    ]
