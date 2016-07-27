# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    BenchmarkDefinitionEntry = apps.get_model('benchmark', 'BenchmarkDefinitionEntry')
    CommandSetEntry = apps.get_model('commandrepo', 'CommandSetEntry')
    CommandEntry = apps.get_model('commandrepo', 'CommandEntry')
    db_alias = schema_editor.connection.alias
    def_entries = BenchmarkDefinitionEntry.objects.using(db_alias).all()

    for def_entry in def_entries:
        com_set = CommandSetEntry.objects.using(db_alias).filter(id=def_entry.command_set.id).first()
        com_entries = CommandEntry.objects.using(db_alias).filter(command_set=com_set)
        for comm in com_entries:
            comm.command = comm.command.replace('{commit}', '{commit_hash}')
            comm.save()


def reverse_func(apps, schema_editor):
    # forwards_func() changes {commit} to {commit_hash}
    # so reverse_func() should revert them.
    BenchmarkDefinitionEntry = apps.get_model('benchmark', 'BenchmarkDefinitionEntry')
    CommandSetEntry = apps.get_model('commandrepo', 'CommandSetEntry')
    CommandEntry = apps.get_model('commandrepo', 'CommandEntry')
    db_alias = schema_editor.connection.alias
    def_entries = BenchmarkDefinitionEntry.objects.using(db_alias).all()

    for def_entry in def_entries:
        com_set = CommandSetEntry.objects.using(db_alias).filter(id=def_entry.command_set.id).first()
        com_entries = CommandEntry.objects.using(db_alias).filter(command_set=com_set)
        for comm in com_entries:
            comm.command = comm.command.replace('{commit_hash}', '{commit}')
            comm.save()

class Migration(migrations.Migration):

    dependencies = [
        ('benchmark', '0007_benchmarkdefinitionentry_max_weeks_old_notify'),
        ('commandrepo', '0005_auto_20151103_2332'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
