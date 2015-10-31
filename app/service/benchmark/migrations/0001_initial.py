# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gitrepo', '0002_gitbranchtrailentry_order'),
        ('commandrepo', '0004_commandgroupentry_user'),
        ('bluesteel', '0007_remove_bluesteellayoutentry_archive'),
    ]

    operations = [
        migrations.CreateModel(
            name='BenchmarkDefinitionEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'Default benchmark name', max_length=128)),
                ('revision', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('command_set', models.ForeignKey(related_name='benchmark_command_set', to='commandrepo.CommandSetEntry')),
                ('layout', models.ForeignKey(related_name='benchmark_layout', to='bluesteel.BluesteelLayoutEntry')),
                ('project', models.ForeignKey(related_name='benchmark_project', to='bluesteel.BluesteelProjectEntry')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BenchmarkExecutionEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('invalidated', models.BooleanField(default=False)),
                ('revision_target', models.IntegerField(default=-1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('commit', models.ForeignKey(related_name='benchmark_exec_commit', to='gitrepo.GitCommitEntry')),
                ('definition', models.ForeignKey(related_name='benchmark_exec_definition', to='benchmark.BenchmarkDefinitionEntry')),
                ('report', models.ForeignKey(related_name='benchmark_exec_command_set', to='commandrepo.CommandSetEntry')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
