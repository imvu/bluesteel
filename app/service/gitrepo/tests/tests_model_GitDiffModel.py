""" Git Diff Model tests """

from django.test import TestCase
from django.test import Client
from django.conf import settings
from django.utils import timezone
from app.service.gitrepo.models.GitProjectModel import GitProjectEntry
from app.service.gitrepo.models.GitDiffModel import GitDiffEntry
from app.service.gitrepo.models.GitCommitModel import GitCommitEntry
from app.service.gitrepo.models.GitUserModel import GitUserEntry
from datetime import timedelta
import os
import hashlib
import shutil


# Create your tests here.

class GitDiffTestCase(TestCase):

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
            author=self.git_user1,
            author_date=timezone.now(),
            committer=self.git_user1,
            committer_date=timezone.now()
        )

        self.git_commit2 = GitCommitEntry.objects.create(
            project=self.git_project1,
            commit_hash='0000200002000020000200002000020000200002',
            author=self.git_user1,
            author_date=timezone.now(),
            committer=self.git_user1,
            committer_date=timezone.now()
        )

    def tearDown(self):
        pass

    def test_create_git_diff_entry(self):
        entry = GitDiffEntry.objects.create(
            project=self.git_project1,
            commit_son=self.git_commit1,
            commit_parent=self.git_commit2,
            content='this is a content of a diff',
        )

        self.assertEqual('http://test/', entry.project.url)
        self.assertEqual('0000100001000010000100001000010000100001', entry.commit_son.commit_hash)
        self.assertEqual('0000200002000020000200002000020000200002', entry.commit_parent.commit_hash)
        self.assertEqual('this is a content of a diff', entry.content)
