# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bluesteel', '0005_auto_20150826_2351'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bluesteellayoutentry',
            name='collect_commits_path',
        ),
    ]
