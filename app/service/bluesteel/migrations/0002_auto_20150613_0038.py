# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bluesteel', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bluesteelcommandentry',
            name='bluesteel_command_set',
        ),
        migrations.DeleteModel(
            name='BluesteelCommandEntry',
        ),
        migrations.RemoveField(
            model_name='bluesteelcommandsetentry',
            name='bluesteel_project',
        ),
        migrations.DeleteModel(
            name='BluesteelCommandSetEntry',
        ),
    ]
