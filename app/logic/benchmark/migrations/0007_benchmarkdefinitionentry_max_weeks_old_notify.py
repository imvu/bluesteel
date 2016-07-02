# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('benchmark', '0006_benchmarkdefinitionentry_max_fluctuation_percent'),
    ]

    operations = [
        migrations.AddField(
            model_name='benchmarkdefinitionentry',
            name='max_weeks_old_notify',
            field=models.IntegerField(default=1),
            preserve_default=True,
        ),
    ]
