""" Git Project Model tests """

from django.test import TestCase
from django.test import Client
from django.conf import settings
from django.utils import timezone
from app.logic.gitrepo.models.GitProjectModel import GitProjectEntry
from app.logic.gitrepo.models.GitCommitModel import GitCommitEntry
from app.logic.gitrepo.models.GitUserModel import GitUserEntry
from app.logic.gitrepo.models.GitBranchModel import GitBranchEntry
from datetime import timedelta
import os
import hashlib
import shutil


# Create your tests here.

class GitProjectTestCase(TestCase):

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

        self.branch_1 = GitBranchEntry.objects.create(
            project=self.git_project1,
            commit=self.git_commit1,
            name='branch-1'
        )

        self.branch_2 = GitBranchEntry.objects.create(
            project=self.git_project1,
            commit=self.git_commit2,
            name='branch-2'
        )

    def tearDown(self):
        pass

    def test_create_git_project_entry(self):
        entry = GitProjectEntry.objects.create(url='http://test/')

        self.assertEqual('http://test/', entry.url)

    def test_project_as_object_returns_branch_info(self):
        obj = self.git_project1.as_object()

        self.assertEqual('http://test/', obj['url'])
        self.assertEqual(2, len(obj['branches']))
        self.assertEqual(self.git_project1.id, obj['branches'][0]['project'])
        self.assertEqual('branch-1', obj['branches'][0]['name'])
        self.assertEqual('0000100001000010000100001000010000100001', obj['branches'][0]['commit_hash'])
        self.assertEqual(self.git_project1.id, obj['branches'][1]['project'])
        self.assertEqual('branch-2', obj['branches'][1]['name'])
        self.assertEqual('0000200002000020000200002000020000200002', obj['branches'][1]['commit_hash'])
