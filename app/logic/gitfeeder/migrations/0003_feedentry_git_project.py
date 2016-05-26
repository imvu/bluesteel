# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gitrepo', '0002_gitbranchtrailentry_order'),
        ('gitfeeder', '0002_feedentry'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedentry',
            name='git_project',
            field=models.ForeignKey(related_name='feed_git_project', blank=True, to='gitrepo.GitProjectEntry', null=True),
            preserve_default=True,
        ),
    ]
