""" GitCommit Model tests """

from django.test import TestCase
from django.test import Client
from django.conf import settings
from django.utils import timezone
from app.service.gitrepo.models.GitProjectModel import GitProjectEntry
from app.service.gitrepo.models.GitCommitModel import GitCommitEntry
from app.service.gitrepo.models.GitUserModel import GitUserEntry
from datetime import timedelta
import os
import hashlib
import shutil


# Create your tests here.

class GitCommitTestCase(TestCase):

    def setUp(self):
        self.git_project1 = GitProjectEntry.objects.create(url='http://test/')

        self.git_user1 = GitUserEntry.objects.create(
            project=self.git_project1,
            name='user1',
            email='user1@test.com'
        )

    def tearDown(self):
        pass

    def test_create_git_commit_entry(self):
        entry = GitCommitEntry.objects.create(
            project=self.git_project1,
            commit_hash='0000100001000010000100001000010000100001',
            git_user=self.git_user1,
            commit_created_at=timezone.now(),
            commit_pushed_at=timezone.now(),
        )

        self.assertEqual('http://test/', entry.project.url)
        self.assertEqual('0000100001000010000100001000010000100001', entry.commit_hash)
        self.assertEqual('user1', self.git_user1.name)
        self.assertEqual('user1@test.com', self.git_user1.email)
        self.assertEqual(True, timezone.now() - timedelta(seconds=5) < entry.commit_created_at)
        self.assertEqual(True, timezone.now() - timedelta(seconds=5) < entry.commit_pushed_at)
