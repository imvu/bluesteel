""" Git Branch Model tests """

from django.test import TestCase
from django.test import Client
from django.conf import settings
from django.utils import timezone
from app.service.gitrepo.models.GitProjectModel import GitProjectEntry
from app.service.gitrepo.models.GitUserModel import GitUserEntry
from app.service.gitrepo.models.GitCommitModel import GitCommitEntry
from app.service.gitrepo.models.GitBranchModel import GitBranchEntry
from datetime import timedelta
import os
import hashlib
import shutil


# Create your tests here.

class GitBranchTestCase(TestCase):

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

    def tearDown(self):
        pass

    def test_create_git_branch_entry(self):
        entry = GitBranchEntry.objects.create(
            project=self.git_project1,
            commit=self.git_commit1,
            name='branch-1'
        )

        self.assertEqual('http://test/', entry.project.url)
        self.assertEqual('branch-1', entry.name)
        self.assertEqual('0000100001000010000100001000010000100001', entry.commit.commit_hash)

    def test_branch_as_object(self):
        entry = GitBranchEntry.objects.create(
            project=self.git_project1,
            commit=self.git_commit1,
            name='branch-1'
        )

        obj = entry.as_object()

        self.assertEqual(self.git_project1.id, obj['project'])
        self.assertEqual('branch-1', obj['name'])
        self.assertEqual('0000100001000010000100001000010000100001', obj['commit_hash'])
