# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2019-11-24 03:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commandrepo', '0005_auto_20151103_2332'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commandentry',
            name='command',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='commandresultentry',
            name='error',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='commandresultentry',
            name='out',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='commandsetentry',
            name='name',
            field=models.TextField(default=''),
        ),
    ]
