# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commandrepo', '0004_commandgroupentry_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commandsetentry',
            name='group',
            field=models.ForeignKey(related_name='command_group', to='commandrepo.CommandGroupEntry', null=True),
            preserve_default=True,
        ),
    ]
