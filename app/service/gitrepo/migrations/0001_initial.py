# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GitBranchEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(default=b'')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GitBranchMergeTargetEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('invalidated', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('current_branch', models.ForeignKey(related_name='git_merge_current_branch', to='gitrepo.GitBranchEntry')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GitBranchTrailEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('branch', models.ForeignKey(related_name='git_trail_branch', to='gitrepo.GitBranchEntry')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GitCommitEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('commit_hash', models.CharField(default=b'0000000000000000000000000000000000000000', max_length=40)),
                ('author_date', models.DateTimeField()),
                ('committer_date', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GitDiffEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField(default=b'')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('commit_parent', models.ForeignKey(related_name='git_diff_commit_parent', to='gitrepo.GitCommitEntry')),
                ('commit_son', models.ForeignKey(related_name='git_diff_commit_son', to='gitrepo.GitCommitEntry')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GitParentEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('parent', models.ForeignKey(related_name='git_parent_commit', to='gitrepo.GitCommitEntry')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GitProjectEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField(max_length=255)),
                ('name', models.CharField(default=b'default-name', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('fetched_at', models.DateTimeField(default=django.utils.timezone.now, auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GitUserEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', max_length=50)),
                ('email', models.EmailField(max_length=75)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('project', models.ForeignKey(related_name='git_user_project', to='gitrepo.GitProjectEntry')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='gitparententry',
            name='project',
            field=models.ForeignKey(related_name='git_parent_project', to='gitrepo.GitProjectEntry'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gitparententry',
            name='son',
            field=models.ForeignKey(related_name='git_son_commit', to='gitrepo.GitCommitEntry'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gitdiffentry',
            name='project',
            field=models.ForeignKey(related_name='git_diff_project', to='gitrepo.GitProjectEntry'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gitcommitentry',
            name='author',
            field=models.ForeignKey(related_name='git_commit_author', to='gitrepo.GitUserEntry'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gitcommitentry',
            name='committer',
            field=models.ForeignKey(related_name='git_commit_committer', to='gitrepo.GitUserEntry'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gitcommitentry',
            name='project',
            field=models.ForeignKey(related_name='git_commit_project', to='gitrepo.GitProjectEntry'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gitbranchtrailentry',
            name='commit',
            field=models.ForeignKey(related_name='git_trail_commit', to='gitrepo.GitCommitEntry'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gitbranchtrailentry',
            name='project',
            field=models.ForeignKey(related_name='git_trail_project', to='gitrepo.GitProjectEntry'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gitbranchmergetargetentry',
            name='diff',
            field=models.ForeignKey(related_name='git_merge_diff', to='gitrepo.GitDiffEntry', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gitbranchmergetargetentry',
            name='project',
            field=models.ForeignKey(related_name='git_merge_project', to='gitrepo.GitProjectEntry'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gitbranchmergetargetentry',
            name='target_branch',
            field=models.ForeignKey(related_name='git_merge_target_branch', to='gitrepo.GitBranchEntry'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gitbranchentry',
            name='commit',
            field=models.ForeignKey(related_name='git_branch_commit', to='gitrepo.GitCommitEntry'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gitbranchentry',
            name='project',
            field=models.ForeignKey(related_name='git_branch_project', to='gitrepo.GitProjectEntry'),
            preserve_default=True,
        ),
    ]
