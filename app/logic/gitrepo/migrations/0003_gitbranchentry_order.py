# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gitrepo', '0002_gitbranchtrailentry_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='gitbranchentry',
            name='order',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
