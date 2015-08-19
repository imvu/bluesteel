# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bluesteel', '0003_bluesteellayoutentry_collect_commits_path'),
    ]

    operations = [
        migrations.AddField(
            model_name='bluesteelprojectentry',
            name='order',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
