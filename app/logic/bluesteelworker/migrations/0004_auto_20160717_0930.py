# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bluesteelworker', '0003_workerentry_max_feed_reports'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workerentry',
            name='description',
            field=models.TextField(default=b'Edit this description!'),
            preserve_default=True,
        ),
    ]
