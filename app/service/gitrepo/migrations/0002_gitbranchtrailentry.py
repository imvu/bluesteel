# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gitrepo', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GitBranchTrailEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('branch', models.ForeignKey(related_name='git_trail_branch', to='gitrepo.GitBranchEntry')),
                ('commit', models.ForeignKey(related_name='git_trail_commit', to='gitrepo.GitCommitEntry')),
                ('project', models.ForeignKey(related_name='git_trail_project', to='gitrepo.GitProjectEntry')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
