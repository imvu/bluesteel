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
            name='GitCommitEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('commit_created_at', models.DateTimeField()),
                ('commit_pushed_at', models.DateTimeField()),
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
                ('git_commit_parent', models.ForeignKey(related_name='git_diff_commit_parent', to='gitrepo.GitCommitEntry')),
                ('git_commit_son', models.ForeignKey(related_name='git_diff_commit_son', to='gitrepo.GitCommitEntry')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GitHashEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('git_hash', models.CharField(default=b'0000000000000000000000000000000000000000', max_length=40)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
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
                ('parent', models.ForeignKey(related_name='git_parent_hash', to='gitrepo.GitHashEntry')),
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
            field=models.ForeignKey(related_name='git_son_hash', to='gitrepo.GitHashEntry'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='githashentry',
            name='project',
            field=models.ForeignKey(related_name='git_hash_project', to='gitrepo.GitProjectEntry'),
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
            name='commit_hash',
            field=models.ForeignKey(related_name='git_commit_hash', to='gitrepo.GitHashEntry'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gitcommitentry',
            name='git_user',
            field=models.ForeignKey(related_name='git_commit_user', to='gitrepo.GitUserEntry'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gitcommitentry',
            name='project',
            field=models.ForeignKey(related_name='git_commit_project', to='gitrepo.GitProjectEntry'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gitbranchentry',
            name='commit_hash',
            field=models.ForeignKey(related_name='git_branch_hash', to='gitrepo.GitHashEntry'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gitbranchentry',
            name='project',
            field=models.ForeignKey(related_name='git_branch_project', to='gitrepo.GitProjectEntry'),
            preserve_default=True,
        ),
    ]
