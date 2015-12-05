# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('commandrepo', '0002_auto_20150726_1535'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='commandentry',
            name='finish_time',
        ),
        migrations.RemoveField(
            model_name='commandentry',
            name='start_time',
        ),
        migrations.AddField(
            model_name='commandresultentry',
            name='finish_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='commandresultentry',
            name='start_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=True,
        ),
    ]
