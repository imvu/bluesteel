# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('benchmark', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='benchmarkexecutionentry',
            name='status',
            field=models.IntegerField(default=0, choices=[(0, b'Ready'), (1, b'In_Progress'), (2, b'Finished')]),
            preserve_default=True,
        ),
    ]
