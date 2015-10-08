# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def make_initial_priorities(apps, schema_editor):
    GitLabProject = apps.get_model('HuskyJamGuru', 'GitLabProject')
    for gitlab_project in GitLabProject.objects.all():
        for i, milestone in enumerate(gitlab_project.gitlab_milestones.all(), 1):
            milestone.priority = i
            milestone.save()


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0026_issuetypeupdate_project'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='gitlabmilestone',
            options={'ordering': ['priority']},
        ),
        migrations.AddField(
            model_name='gitlabmilestone',
            name='priority',
            field=models.IntegerField(default=1, editable=False),
            preserve_default=False,
        ),
        migrations.RunPython(make_initial_priorities),
    ]
