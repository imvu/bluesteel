# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bluesteel', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='bluesteelcommandentry',
            name='bluesteel_command_set',
            field=models.ForeignKey(related_name='bluesteel_command_set', to='bluesteel.BluesteelCommandSetEntry', null=True),
            preserve_default=True,
        ),
    ]
