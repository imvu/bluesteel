# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('commandrepo', '0003_auto_20150726_2320'),
    ]

    operations = [
        migrations.AddField(
            model_name='commandgroupentry',
            name='user',
            field=models.ForeignKey(related_name='command_group_user', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]
