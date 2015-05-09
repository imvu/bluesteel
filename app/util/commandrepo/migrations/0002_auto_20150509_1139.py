# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commandrepo', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commandentry',
            name='status',
            field=models.IntegerField(default=0, choices=[(0, b'Ok'), (1, b'Error')]),
            preserve_default=True,
        ),
    ]
