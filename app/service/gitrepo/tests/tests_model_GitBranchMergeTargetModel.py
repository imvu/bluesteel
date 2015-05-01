""" Git Branch Merge Target Model tests """

from django.test import TestCase
from django.test import Client
from django.conf import settings
from django.utils import timezone
from app.service.gitrepo.models.GitProjectModel import GitProjectEntry
from app.service.gitrepo.models.GitBranchModel import GitBranchEntry
from app.service.gitrepo.models.GitCommitModel import GitCommitEntry
from app.service.gitrepo.models.GitUserModel import GitUserEntry
from app.service.gitrepo.models.GitDiffModel import GitDiffEntry
from app.service.gitrepo.models.GitBranchMergeTargetModel import GitBranchMergeTargetEntry
from datetime import timedelta
import os
import hashlib
import shutil


# Create your tests here.

class GitBranchMergeTargetTestCase(TestCase):

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

        self.git_branch1 = GitBranchEntry.objects.create(
            project=self.git_project1,
            commit=self.git_commit1,
            name='branch1'
        )

        self.git_branch2 = GitBranchEntry.objects.create(
            project=self.git_project1,
            commit=self.git_commit2,
            name='branch2'
        )

        self.git_diff1 = GitDiffEntry.objects.create(
            project=self.git_project1,
            commit_son=self.git_commit1,
            commit_parent=self.git_commit2,
            content='content-text'
        )


    def tearDown(self):
        pass

    def test_create_git_branch_merge_target_entry(self):
        entry = GitBranchMergeTargetEntry.objects.create(
            project=self.git_project1,
            current_branch=self.git_branch1,
            target_branch=self.git_branch2,
            diff=self.git_diff1,
        )

        self.assertEqual('http://test/', entry.project.url)
        self.assertEqual('branch1', entry.current_branch.name)
        self.assertEqual('branch2', entry.target_branch.name)
        self.assertEqual('content-text', entry.diff.content)
        self.assertEqual(False, entry.invalidated)
