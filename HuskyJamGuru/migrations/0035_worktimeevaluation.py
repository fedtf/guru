# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0034_auto_20151101_1109'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkTimeEvaluation',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('type', models.CharField(max_length=100, choices=[('markup', 'Markup'), ('backend', 'Backend'), ('ux', 'UX'), ('business-analyse', 'Business Analyse'), ('design', 'Design'), ('management', 'Management')])),
                ('time', models.IntegerField()),
                ('project', models.ForeignKey(related_name='work_time_evaluations', to='HuskyJamGuru.Project')),
            ],
        ),
    ]
