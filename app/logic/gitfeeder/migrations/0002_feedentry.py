# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commandrepo', '0005_auto_20151103_2332'),
        ('bluesteelworker', '0002_workerentry_git_feeder'),
        ('gitfeeder', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeedEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('command_group', models.ForeignKey(related_name='feed_command_group', to='commandrepo.CommandGroupEntry')),
                ('worker', models.ForeignKey(related_name='feed_worker', blank=True, to='bluesteelworker.WorkerEntry', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
