# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bluesteelworker', '0002_workerentry_git_feeder'),
        ('benchmark', '0002_benchmarkexecutionentry_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='benchmarkexecutionentry',
            name='worker',
            field=models.ForeignKey(related_name='benchmark_exec_worker', to='bluesteelworker.WorkerEntry', null=True),
            preserve_default=True,
        ),
    ]
