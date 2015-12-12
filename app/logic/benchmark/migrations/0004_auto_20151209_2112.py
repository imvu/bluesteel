# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('benchmark', '0003_benchmarkexecutionentry_worker'),
    ]

    operations = [
        migrations.AlterField(
            model_name='benchmarkexecutionentry',
            name='worker',
            field=models.ForeignKey(related_name='benchmark_exec_worker', to='bluesteelworker.WorkerEntry'),
            preserve_default=True,
        ),
    ]
