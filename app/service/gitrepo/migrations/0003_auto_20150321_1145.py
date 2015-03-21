# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gitrepo', '0002_gitbranchmergetargetentry'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gitbranchmergetargetentry',
            name='diff',
            field=models.ForeignKey(related_name='git_merge_diff', to='gitrepo.GitDiffEntry', null=True),
            preserve_default=True,
        ),
    ]
