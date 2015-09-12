# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0002_auto_20150805_1813'),
    ]

    operations = [
        migrations.CreateModel(
            name='GitlabModelExtension',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('gitlab_id', models.IntegerField(unique=True, blank=None)),
            ],
        ),
        migrations.RemoveField(
            model_name='project',
            name='gitlab_id',
        ),
        migrations.RemoveField(
            model_name='project',
            name='id',
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('gitlabmodelextension_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='HuskyJamGuru.GitlabModelExtension')),
                ('name', models.CharField(default=b'Can not load =(', max_length=500)),
            ],
            bases=('HuskyJamGuru.gitlabmodelextension',),
        ),
        migrations.AddField(
            model_name='project',
            name='gitlabmodelextension_ptr',
            field=models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, default=1, serialize=False, to='HuskyJamGuru.GitlabModelExtension'),
            preserve_default=False,
        ),
    ]
