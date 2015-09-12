# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0003_auto_20150912_1747'),
    ]

    operations = [
        migrations.CreateModel(
            name='GitlabProject',
            fields=[
                ('gitlabmodelextension_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='HuskyJamGuru.GitlabModelExtension')),
            ],
            bases=('HuskyJamGuru.gitlabmodelextension',),
        ),
        migrations.RemoveField(
            model_name='project',
            name='gitlabmodelextension_ptr',
        ),
        migrations.AddField(
            model_name='project',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(default=b'', max_length=500),
        ),
        migrations.AddField(
            model_name='gitlabproject',
            name='project',
            field=models.ForeignKey(to='HuskyJamGuru.Project'),
        ),
    ]
