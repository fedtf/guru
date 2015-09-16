# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0003_auto_20150913_1720'),
    ]

    operations = [
        migrations.AddField(
            model_name='gitlabissue',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 13, 17, 22, 43, 569282, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
