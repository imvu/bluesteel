# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bluesteel', '0006_remove_bluesteellayoutentry_collect_commits_path'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bluesteellayoutentry',
            name='archive',
        ),
    ]
