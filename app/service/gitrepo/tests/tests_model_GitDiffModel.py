""" Git Diff Model tests """

from django.test import TestCase
from django.test import Client
from django.conf import settings
from django.utils import timezone
from app.service.gitrepo.models.GitProjectModel import GitProjectEntry
from app.service.gitrepo.models.GitHashModel import GitHashEntry
from app.service.gitrepo.models.GitDiffModel import GitDiffEntry
from datetime import timedelta
import os
import hashlib
import shutil


# Create your tests here.

class GitDiffTestCase(TestCase):

    def setUp(self):
        self.git_project1 = GitProjectEntry.objects.create(url='http://test/')

    def tearDown(self):
        pass

    def test_create_git_diff_entry(self):
        entry = GitDiffEntry.objects.create(
            project=self.git_project1,
            content='this is a content of a diff',
        )

        self.assertEqual('http://test/', entry.project.url)
        self.assertEqual('this is a content of a diff', entry.content)
