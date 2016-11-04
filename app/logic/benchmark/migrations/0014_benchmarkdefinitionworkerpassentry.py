# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-11-04 05:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bluesteelworker', '0005_workerfileshashentry'),
        ('benchmark', '0013_auto_20161102_1609'),
    ]

    operations = [
        migrations.CreateModel(
            name='BenchmarkDefinitionWorkerPassEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('allowed', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('definition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='worker_pass_definition', to='benchmark.BenchmarkDefinitionEntry')),
                ('worker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='worker_pass_worker', to='bluesteelworker.WorkerEntry')),
            ],
        ),
    ]
