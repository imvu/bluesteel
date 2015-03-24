# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gitrepo', '0003_auto_20150321_1145'),
    ]

    operations = [
        migrations.AddField(
            model_name='gitbranchmergetargetentry',
            name='invalidated',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
