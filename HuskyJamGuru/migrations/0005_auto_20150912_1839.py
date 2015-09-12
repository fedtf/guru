# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('HuskyJamGuru', '0004_auto_20150912_1815'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProjectAccess',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=100)),
                ('project', models.ForeignKey(related_name='user_project_accesses', to='HuskyJamGuru.Project')),
                ('user', models.ForeignKey(related_name='notifications_settings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='gitlabproject',
            name='project',
            field=models.ForeignKey(related_name='gitlab_projects', to='HuskyJamGuru.Project'),
        ),
    ]
