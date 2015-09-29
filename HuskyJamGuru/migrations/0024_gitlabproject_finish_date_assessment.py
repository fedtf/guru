# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('HuskyJamGuru', '0023_auto_20150929_1028'),
    ]

    operations = [
        migrations.AddField(
            model_name='gitlabproject',
            name='finish_date_assessment',
            field=models.DateField(default=datetime.datetime(2015, 9, 29, 14, 17, 52, 717799, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
