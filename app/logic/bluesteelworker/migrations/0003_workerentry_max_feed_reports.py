# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bluesteelworker', '0002_workerentry_git_feeder'),
    ]

    operations = [
        migrations.AddField(
            model_name='workerentry',
            name='max_feed_reports',
            field=models.IntegerField(default=100),
            preserve_default=True,
        ),
    ]
