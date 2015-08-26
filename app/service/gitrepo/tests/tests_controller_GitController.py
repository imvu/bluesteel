""" Git Controller tests """

from django.test import TestCase
from django.utils import timezone
from app.service.gitrepo.models.GitParentModel import GitParentEntry
from app.service.gitrepo.models.GitCommitModel import GitCommitEntry
from app.service.gitrepo.models.GitBranchModel import GitBranchEntry
from app.service.gitrepo.models.GitBranchTrailModel import GitBranchTrailEntry
from app.service.gitrepo.models.GitBranchMergeTargetModel import GitBranchMergeTargetEntry
from app.service.gitrepo.models.GitUserModel import GitUserEntry
from app.service.gitrepo.models.GitDiffModel import GitDiffEntry
from app.service.gitrepo.models.GitProjectModel import GitProjectEntry
from app.service.gitrepo.controllers.GitController import GitController
from datetime import timedelta


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

        self.git_parent = GitParentEntry.objects.create(
            project=self.git_project1,
            parent=self.git_commit1,
            son=self.git_commit2
        )

        self.git_merge_target = GitBranchMergeTargetEntry.objects.create(
            project=self.git_project1,
            current_branch=self.git_branch1,
            target_branch=self.git_branch2,
            fork_point=self.git_commit1,
            diff=self.git_diff1
        )

        self.git_trail = GitBranchTrailEntry.objects.create(
            project=self.git_project1,
            branch=self.git_branch1,
            commit=self.git_commit1
        )


    def tearDown(self):
        pass

    def test_delete_git_project(self):
        self.assertEqual(1, GitProjectEntry.objects.all().count())
        self.assertEqual(1, GitUserEntry.objects.all().count())
        self.assertEqual(2, GitCommitEntry.objects.all().count())
        self.assertEqual(1, GitDiffEntry.objects.all().count())
        self.assertEqual(2, GitBranchEntry.objects.all().count())
        self.assertEqual(1, GitParentEntry.objects.all().count())
        self.assertEqual(1, GitBranchMergeTargetEntry.objects.all().count())
        self.assertEqual(1, GitBranchTrailEntry.objects.all().count())

        GitController.delete_git_project(self.git_project1)

        self.assertEqual(0, GitProjectEntry.objects.all().count())
        self.assertEqual(0, GitUserEntry.objects.all().count())
        self.assertEqual(0, GitCommitEntry.objects.all().count())
        self.assertEqual(0, GitDiffEntry.objects.all().count())
        self.assertEqual(0, GitBranchEntry.objects.all().count())
        self.assertEqual(0, GitParentEntry.objects.all().count())
        self.assertEqual(0, GitBranchMergeTargetEntry.objects.all().count())
        self.assertEqual(0, GitBranchTrailEntry.objects.all().count())
