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


    def tearDown(self):
        pass

    def create_commit(self, project, user, hash_num):
        del self
        commit_hash = str('{0:05d}'.format(hash_num) * 8)
        git_commit = GitCommitEntry.objects.create(
            project=project,
            commit_hash=commit_hash,
            author=user,
            author_date=timezone.now(),
            committer=user,
            committer_date=timezone.now()
        )
        return git_commit

    def test_delete_git_project(self):
        git_commit1 = GitCommitEntry.objects.create(
            project=self.git_project1,
            commit_hash='0000100001000010000100001000010000100001',
            author=self.git_user1,
            author_date=timezone.now(),
            committer=self.git_user1,
            committer_date=timezone.now()
        )

        git_commit2 = GitCommitEntry.objects.create(
            project=self.git_project1,
            commit_hash='0000200002000020000200002000020000200002',
            author=self.git_user1,
            author_date=timezone.now(),
            committer=self.git_user1,
            committer_date=timezone.now()
        )

        git_branch1 = GitBranchEntry.objects.create(
            project=self.git_project1,
            commit=git_commit1,
            name='branch1'
        )

        git_branch2 = GitBranchEntry.objects.create(
            project=self.git_project1,
            commit=git_commit2,
            name='branch2'
        )

        git_diff1 = GitDiffEntry.objects.create(
            project=self.git_project1,
            commit_son=git_commit1,
            commit_parent=git_commit2,
            content='content-text'
        )

        git_parent = GitParentEntry.objects.create(
            project=self.git_project1,
            parent=git_commit1,
            son=git_commit2
        )

        git_merge_target = GitBranchMergeTargetEntry.objects.create(
            project=self.git_project1,
            current_branch=git_branch1,
            target_branch=git_branch2,
            fork_point=git_commit1,
            diff=git_diff1
        )

        git_trail = GitBranchTrailEntry.objects.create(
            project=self.git_project1,
            branch=git_branch1,
            commit=git_commit1
        )

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

    def test_branches_trimmed_by_merge_target(self):
        #  3   5
        #  2 - 4
        #  1
        # Commits
        git_commit1 = self.create_commit(self.git_project1, self.git_user1, 1)
        git_commit2 = self.create_commit(self.git_project1, self.git_user1, 2)
        git_commit3 = self.create_commit(self.git_project1, self.git_user1, 3)
        git_commit4 = self.create_commit(self.git_project1, self.git_user1, 4)
        git_commit5 = self.create_commit(self.git_project1, self.git_user1, 5)

        # Branches
        git_branch1 = GitBranchEntry.objects.create(
            project=self.git_project1,
            commit=git_commit3,
            name='branch1'
        )

        git_branch2 = GitBranchEntry.objects.create(
            project=self.git_project1,
            commit=git_commit5,
            name='branch2'
        )

        # Parents
        git_parent_1_2 = GitParentEntry.objects.create(
            project=self.git_project1,
            parent=git_commit1,
            son=git_commit2
        )

        git_parent_2_3 = GitParentEntry.objects.create(
            project=self.git_project1,
            parent=git_commit2,
            son=git_commit3
        )

        git_parent_4_5 = GitParentEntry.objects.create(
            project=self.git_project1,
            parent=git_commit4,
            son=git_commit5
        )

        git_parent_2_4 = GitParentEntry.objects.create(
            project=self.git_project1,
            parent=git_commit2,
            son=git_commit4
        )

        # Diffs
        git_diff1 = GitDiffEntry.objects.create(
            project=self.git_project1,
            commit_son=git_commit5,
            commit_parent=git_commit2,
            content='content-text'
        )

        # Merge targets
        git_merge_target_2_1 = GitBranchMergeTargetEntry.objects.create(
            project=self.git_project1,
            current_branch=git_branch2,
            target_branch=git_branch1,
            fork_point=git_commit2,
            diff=git_diff1
        )

        git_merge_target_1_1 = GitBranchMergeTargetEntry.objects.create(
            project=self.git_project1,
            current_branch=git_branch1,
            target_branch=git_branch1,
            fork_point=git_commit1,
            diff=git_diff1
        )

        #Trails Branch 1
        git_trail_1_1 = GitBranchTrailEntry.objects.create(
            project=self.git_project1,
            branch=git_branch1,
            commit=git_commit3,
            order=0
        )

        git_trail_1_2 = GitBranchTrailEntry.objects.create(
            project=self.git_project1,
            branch=git_branch1,
            commit=git_commit2,
            order=1
        )

        git_trail_1_3 = GitBranchTrailEntry.objects.create(
            project=self.git_project1,
            branch=git_branch1,
            commit=git_commit1,
            order=3
        )

        #Trails Branch 2
        git_trail_2_1 = GitBranchTrailEntry.objects.create(
            project=self.git_project1,
            branch=git_branch2,
            commit=git_commit5,
            order=0
        )

        git_trail_2_2 = GitBranchTrailEntry.objects.create(
            project=self.git_project1,
            branch=git_branch2,
            commit=git_commit4,
            order=1
        )

        git_trail_2_3 = GitBranchTrailEntry.objects.create(
            project=self.git_project1,
            branch=git_branch2,
            commit=git_commit2,
            order=2
        )

        git_trail_2_4 = GitBranchTrailEntry.objects.create(
            project=self.git_project1,
            branch=git_branch2,
            commit=git_commit1,
            order=3
        )

        branches_trimmed = GitController.get_branches_trimmed_by_merge_target(self.git_project1)

        self.assertEqual(2 , len(branches_trimmed))

        self.assertEqual('branch1' , branches_trimmed[0]['name'])
        self.assertEqual(3 , len(branches_trimmed[0]['commits']))
        self.assertEqual('0000300003000030000300003000030000300003', branches_trimmed[0]['commits'][0]['hash'])
        self.assertEqual('0000200002000020000200002000020000200002', branches_trimmed[0]['commits'][1]['hash'])
        self.assertEqual('0000100001000010000100001000010000100001', branches_trimmed[0]['commits'][2]['hash'])

        self.assertEqual(2 , len(branches_trimmed[1]['commits']))
        self.assertEqual('branch2' , branches_trimmed[1]['name'])
        self.assertEqual('0000500005000050000500005000050000500005', branches_trimmed[1]['commits'][0]['hash'])
        self.assertEqual('0000400004000040000400004000040000400004', branches_trimmed[1]['commits'][1]['hash'])
