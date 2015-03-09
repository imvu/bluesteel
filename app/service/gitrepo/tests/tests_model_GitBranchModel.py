""" Git Branch Model tests """

from django.test import TestCase
from django.test import Client
from django.conf import settings
from django.utils import timezone
from app.service.gitrepo.models.GitProjectModel import GitProjectEntry
from app.service.gitrepo.models.GitHashModel import GitHashEntry
from app.service.gitrepo.models.GitBranchModel import GitBranchEntry
from datetime import timedelta
import os
import hashlib
import shutil


# Create your tests here.

class GitBranchTestCase(TestCase):

    def setUp(self):
        self.git_project1 = GitProjectEntry.objects.create(url='http://test/')

        self.git_hash1 = GitHashEntry.objects.create(
            project=self.git_project1,
            git_hash='0000100001000010000100001000010000100001'
        )

    def tearDown(self):
        pass

    def test_create_git_branch_entry(self):
        entry = GitBranchEntry.objects.create(
            project=self.git_project1,
            commit_hash=self.git_hash1,
        )

        self.assertEqual('http://test/', entry.project.url)
        self.assertEqual('0000100001000010000100001000010000100001', entry.commit_hash.git_hash)
