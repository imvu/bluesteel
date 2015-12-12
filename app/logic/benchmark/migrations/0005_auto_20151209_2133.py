# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('benchmark', '0004_auto_20151209_2112'),
    ]

    operations = [
        migrations.AlterField(
            model_name='benchmarkexecutionentry',
            name='worker',
            field=models.ForeignKey(related_name='benchmark_exec_worker', to='bluesteelworker.WorkerEntry', null=True),
            preserve_default=True,
        ),
    ]
