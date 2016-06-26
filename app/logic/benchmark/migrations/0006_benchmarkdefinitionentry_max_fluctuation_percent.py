# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('benchmark', '0005_auto_20151209_2133'),
    ]

    operations = [
        migrations.AddField(
            model_name='benchmarkdefinitionentry',
            name='max_fluctuation_percent',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
