# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2019-11-24 03:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logger', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logentry',
            name='log_type',
            field=models.IntegerField(choices=[(0, 'Debug'), (1, 'Info'), (2, 'Warning'), (3, 'Error'), (4, 'Critical')], default=1),
        ),
        migrations.AlterField(
            model_name='logentry',
            name='message',
            field=models.TextField(default=''),
        ),
    ]