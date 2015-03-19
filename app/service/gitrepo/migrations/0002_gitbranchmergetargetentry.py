# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gitrepo', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GitBranchMergeTargetEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('current_branch', models.ForeignKey(related_name='git_merge_current_branch', to='gitrepo.GitBranchEntry')),
                ('diff', models.ForeignKey(related_name='git_merge_diff', to='gitrepo.GitDiffEntry')),
                ('project', models.ForeignKey(related_name='git_merge_project', to='gitrepo.GitProjectEntry')),
                ('target_branch', models.ForeignKey(related_name='git_merge_target_branch', to='gitrepo.GitBranchEntry')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
