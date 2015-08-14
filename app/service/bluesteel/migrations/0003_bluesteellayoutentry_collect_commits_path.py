# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bluesteel', '0002_auto_20150613_0038'),
    ]

    operations = [
        migrations.AddField(
            model_name='bluesteellayoutentry',
            name='collect_commits_path',
            field=models.CharField(default=b'', max_length=50),
            preserve_default=True,
        ),
    ]
