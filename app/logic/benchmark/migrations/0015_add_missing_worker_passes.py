# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def forwards_func(apps, schema_editor):
    # We need to populate all the Benchmark Definition Worker Passes
    BenchmarkDefinitionEntry = apps.get_model('benchmark', 'BenchmarkDefinitionEntry')
    BenchmarkDefinitionWorkerPassEntry = apps.get_model('benchmark', 'BenchmarkDefinitionWorkerPassEntry')
    WorkerEntry = apps.get_model('bluesteelworker', 'WorkerEntry')
    db_alias = schema_editor.connection.alias
    def_entries = BenchmarkDefinitionEntry.objects.using(db_alias).all()
    worker_entries = WorkerEntry.objects.using(db_alias).all()

    for def_entry in def_entries:
        for worker in worker_entries:
            BenchmarkDefinitionWorkerPassEntry.objects.using(db_alias).create(definition=def_entry, worker=worker)


def reverse_func(apps, schema_editor):
    # I think we need to do nothing here because it does not matter at this point if
    # Benchmark Deginition Worker Passes exists.
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('benchmark', '0014_benchmarkdefinitionworkerpassentry'),
        ('bluesteelworker', '0005_workerfileshashentry'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
