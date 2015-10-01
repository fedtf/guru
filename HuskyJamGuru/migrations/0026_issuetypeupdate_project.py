# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def connect_issues_type_changes_with_projects(apps, schema_editor):
    IssueTypeUpdate = apps.get_model("HuskyJamGuru", "IssueTypeUpdate")
    for type_change in IssueTypeUpdate.objects.all():
        project = type_change.gitlab_issue.gitlab_project.project
        type_change.project = project
        type_change.save()

class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0025_auto_20150930_1112'),
    ]

    operations = [
        migrations.AddField(
            model_name='issuetypeupdate',
            name='project',
            field=models.ForeignKey(to='HuskyJamGuru.Project', related_name='issues_type_updates', default=1),
            preserve_default=False,
        ),
        migrations.RunPython(connect_issues_type_changes_with_projects)
    ]
