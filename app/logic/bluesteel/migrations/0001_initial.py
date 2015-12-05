# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gitrepo', '0001_initial'),
        ('commandrepo', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BluesteelCommandEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField(default=0)),
                ('command', models.CharField(default=b'', max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BluesteelCommandSetEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('command_set_type', models.IntegerField(default=0, choices=[(0, b'CLONE'), (1, b'FETCH')])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BluesteelLayoutEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', max_length=50)),
                ('archive', models.CharField(default=b'', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BluesteelProjectEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('command_group', models.ForeignKey(related_name='bluesteel_command_group', to='commandrepo.CommandGroupEntry')),
                ('git_project', models.ForeignKey(related_name='bluesteel_git_project', to='gitrepo.GitProjectEntry')),
                ('layout', models.ForeignKey(related_name='bluesteel_layout', to='bluesteel.BluesteelLayoutEntry')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='bluesteelcommandsetentry',
            name='bluesteel_project',
            field=models.ForeignKey(related_name='bluesteel_project', to='bluesteel.BluesteelProjectEntry'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bluesteelcommandentry',
            name='bluesteel_command_set',
            field=models.ForeignKey(related_name='bluesteel_command_set', to='bluesteel.BluesteelCommandSetEntry'),
            preserve_default=True,
        ),
    ]
