# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bluesteel', '0007_remove_bluesteellayoutentry_archive'),
    ]

    operations = [
        migrations.AddField(
            model_name='bluesteelprojectentry',
            name='git_project_folder_search_path',
            field=models.CharField(default=b'.', max_length=255),
            preserve_default=True,
        ),
    ]
