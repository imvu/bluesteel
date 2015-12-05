# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bluesteel', '0004_bluesteelprojectentry_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='bluesteellayoutentry',
            name='active',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bluesteellayoutentry',
            name='project_index_path',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
