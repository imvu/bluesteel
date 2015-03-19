""" Git Parent Model tests """

from django.test import TestCase
from django.test import Client
from django.conf import settings
from django.utils import timezone
from app.service.gitrepo.models.GitProjectModel import GitProjectEntry
from app.service.gitrepo.models.GitCommitModel import GitCommitEntry
from app.service.gitrepo.models.GitUserModel import GitUserEntry
from app.service.gitrepo.models.GitParentModel import GitParentEntry
from datetime import timedelta
import os
import hashlib
import shutil


# Create your tests here.

class GitParentTestCase(TestCase):

    def setUp(self):
        self.git_project1 = GitProjectEntry.objects.create(url='http://test/')

        self.git_user1 = GitUserEntry.objects.create(
            project=self.git_project1,
            name='user1',
            email='user1@test.com'
        )

        self.git_commit1 = GitCommitEntry.objects.create(
            project=self.git_project1,
            commit_hash='0000100001000010000100001000010000100001',
            git_user=self.git_user1,
            commit_created_at=timezone.now(),
            commit_pushed_at=timezone.now(),
        )

        self.git_commit2 = GitCommitEntry.objects.create(
            project=self.git_project1,
            commit_hash='0000200002000020000200002000020000200002',
            git_user=self.git_user1,
            commit_created_at=timezone.now(),
            commit_pushed_at=timezone.now(),
        )

    def tearDown(self):
        pass

    def test_create_git_parent_entry(self):
        entry = GitParentEntry.objects.create(
            project=self.git_project1,
            parent=self.git_commit1,
            son=self.git_commit2,
            order=5
        )

        self.assertEqual('http://test/', entry.project.url)
        self.assertEqual('0000100001000010000100001000010000100001', entry.parent.commit_hash)
        self.assertEqual('0000200002000020000200002000020000200002', entry.son.commit_hash)
        self.assertEqual(5, entry.order)

    def test_create_git_parent_default(self):
        entry = GitParentEntry.objects.create(
            project=self.git_project1,
            parent=self.git_commit1,
            son=self.git_commit2,
        )

        self.assertEqual(0, entry.order)