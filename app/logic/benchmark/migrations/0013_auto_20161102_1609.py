# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-11-02 23:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmark', '0012_benchmarkdefinitionentry_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='benchmarkfluctuationoverrideentry',
            name='result_id',
            field=models.CharField(default=b'', max_length=255),
        ),
    ]
