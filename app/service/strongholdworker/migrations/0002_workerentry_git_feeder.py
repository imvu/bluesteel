# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('strongholdworker', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='workerentry',
            name='git_feeder',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
