""" Git Feed Views branch tests """

from django.test import TestCase
from django.test import Client
from django.conf import settings
from django.utils import timezone
from app.logic.gitrepo.models.GitProjectModel import GitProjectEntry
from app.logic.gitrepo.models.GitUserModel import GitUserEntry
from app.logic.gitrepo.models.GitCommitModel import GitCommitEntry
from app.logic.gitrepo.models.GitParentModel import GitParentEntry
from app.logic.gitrepo.models.GitDiffModel import GitDiffEntry
from app.logic.gitrepo.models.GitBranchModel import GitBranchEntry
from app.logic.gitrepo.models.GitBranchTrailModel import GitBranchTrailEntry
from app.logic.gitrepo.models.GitBranchMergeTargetModel import GitBranchMergeTargetEntry
from app.logic.gitfeeder.helper import FeederTestHelper
from app.logic.httpcommon import res
from datetime import timedelta
import json
import os
import hashlib
import shutil

# Create your tests here.

class GitFeedViewsBranchTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.git_project1 = GitProjectEntry.objects.create(url='http://test/')
        self.git_user1 = GitUserEntry.objects.create(
            project=self.git_project1,
            name='user1',
            email='user1@test.com'
        )


    def tearDown(self):
        pass

    def test_incorrect_branch(self):
        commit_time = str(timezone.now().isoformat())
        commit1 = FeederTestHelper.create_commit(1, [], 'user1', 'user1@test.com', commit_time, commit_time)

        branch1 = FeederTestHelper.create_branch('master', 2, 'master', 2, 1, [2, 1], 'merge-target-content')

        feed_data = {}
        feed_data['commits'] = []
        feed_data['commits'].append(commit1)
        feed_data['branches'] = []
        feed_data['branches'].append(branch1)
        feed_data['diffs'] = []
        feed_data['diffs'].append(FeederTestHelper.create_diff(1, 1, 'diff-1'))

        post_data = FeederTestHelper.create_feed_data_and_report(
            feed_data,
            FeederTestHelper.get_default_report(1)
        )

        resp = self.client.post(
            '/main/feed/commit/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(post_data),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(400, resp_obj['status'])
        self.assertEqual('Branches not correct', resp_obj['message'])
        self.assertEqual(0, GitCommitEntry.objects.all().count())
        self.assertEqual(0, GitBranchEntry.objects.all().count())

    def test_branches_are_deleted_if_not_in_feed_data(self):
        commit_a = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000100001000010000100001000010000100001', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())
        commit_b = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000200002000020000200002000020000200002', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())

        branch_a = GitBranchEntry.objects.create(project=self.git_project1, name='branch-old', commit=commit_a)

        trail_a = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch_a, commit=commit_a)
        trail_b = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch_a, commit=commit_b)

        commit_time = str(timezone.now().isoformat())
        commit1 = FeederTestHelper.create_commit(5, [], 'user1', 'user1@test.com', commit_time, commit_time)
        commit2 = FeederTestHelper.create_commit(6, [], 'user1', 'user1@test.com', commit_time, commit_time)

        branch1 = FeederTestHelper.create_branch('master', 5, 'master', 5, 5, [5], 'merge-target-content')
        branch2 = FeederTestHelper.create_branch('branch2', 6, 'branch2', 6, 6, [6], 'merge-target-content')

        feed_data = {}
        feed_data['commits'] = []
        feed_data['commits'].append(commit1)
        feed_data['commits'].append(commit2)
        feed_data['branches'] = []
        feed_data['branches'].append(branch1)
        feed_data['branches'].append(branch2)
        feed_data['diffs'] = []
        feed_data['diffs'].append(FeederTestHelper.create_diff(6, 5, 'diff-1'))

        self.assertEqual(1, GitCommitEntry.objects.filter(project=self.git_project1, commit_hash='0000100001000010000100001000010000100001').count())
        self.assertEqual(1, GitCommitEntry.objects.filter(project=self.git_project1, commit_hash='0000200002000020000200002000020000200002').count())
        self.assertEqual(1, GitBranchEntry.objects.filter(project=self.git_project1, name='branch-old').count())
        self.assertEqual(1, GitBranchTrailEntry.objects.filter(project=self.git_project1, branch=branch_a, commit=commit_a).count())
        self.assertEqual(1, GitBranchTrailEntry.objects.filter(project=self.git_project1, branch=branch_a, commit=commit_b).count())

        post_data = FeederTestHelper.create_feed_data_and_report(
            feed_data,
            FeederTestHelper.get_default_report(1)
        )

        resp = self.client.post(
            '/main/feed/commit/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(post_data),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual(0, GitCommitEntry.objects.filter(project=self.git_project1, commit_hash='0000100001000010000100001000010000100001').count())
        self.assertEqual(0, GitCommitEntry.objects.filter(project=self.git_project1, commit_hash='0000200002000020000200002000020000200002').count())
        self.assertEqual(0, GitBranchEntry.objects.filter(project=self.git_project1, name='branch-old').count())
        self.assertEqual(0, GitBranchTrailEntry.objects.filter(project=self.git_project1, branch=branch_a, commit=commit_a).count())
        self.assertEqual(0, GitBranchTrailEntry.objects.filter(project=self.git_project1, branch=branch_a, commit=commit_b).count())

        self.assertEqual(1, GitCommitEntry.objects.filter(project=self.git_project1, commit_hash='0000500005000050000500005000050000500005').count())
        self.assertEqual(1, GitCommitEntry.objects.filter(project=self.git_project1, commit_hash='0000600006000060000600006000060000600006').count())
        self.assertEqual(1, GitBranchEntry.objects.filter(project=self.git_project1, name='master').count())
        self.assertEqual(1, GitBranchEntry.objects.filter(project=self.git_project1, name='branch2').count())


    def test_branch_update_and_no_merge_target(self):
        commit_entry = GitCommitEntry.objects.create(
            project=self.git_project1,
            commit_hash=FeederTestHelper.hash_string(1),
            author=self.git_user1,
            author_date=timezone.now(),
            committer=self.git_user1,
            committer_date=timezone.now()
            )

        branch_entry = GitBranchEntry.objects.create(
            project=self.git_project1,
            name='master',
            commit=commit_entry
            )

        commit_time = str(timezone.now().isoformat())
        commit1 = FeederTestHelper.create_commit(2, [1], 'user1', 'user1@test.com', commit_time, commit_time)

        branch1 = FeederTestHelper.create_branch('master', 2, 'master', 2, 2, [2, 1], 'merge-target-content')

        feed_data = {}
        feed_data['commits'] = []
        feed_data['commits'].append(commit1)
        feed_data['branches'] = []
        feed_data['branches'].append(branch1)
        feed_data['diffs'] = []
        feed_data['diffs'].append(FeederTestHelper.create_diff(2, 1, 'diff-2-1'))

        post_data = FeederTestHelper.create_feed_data_and_report(
            feed_data,
            FeederTestHelper.get_default_report(1)
        )

        resp = self.client.post(
            '/main/feed/commit/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(post_data),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual(2, GitCommitEntry.objects.all().count())
        self.assertEqual(1, GitBranchEntry.objects.all().count())
        self.assertEqual(1, GitParentEntry.objects.all().count())
        self.assertEqual(2, GitDiffEntry.objects.all().count())
        self.assertEqual(2, GitBranchTrailEntry.objects.all().count())
        self.assertEqual(1, GitBranchMergeTargetEntry.objects.all().count())

        self.assertIsNotNone(GitCommitEntry.objects.filter(commit_hash='0000100001000010000100001000010000100001').first())
        self.assertIsNotNone(GitCommitEntry.objects.filter(commit_hash='0000200002000020000200002000020000200002').first())

        self.assertIsNotNone(GitParentEntry.objects.filter(parent__commit_hash='0000100001000010000100001000010000100001').first())

        branch = GitBranchEntry.objects.filter(name='master').first()
        self.assertEqual(self.git_project1.id, branch.project.id)
        self.assertEqual('master', branch.name)
        self.assertEqual('0000200002000020000200002000020000200002', branch.commit.commit_hash)

        trail1 = GitBranchTrailEntry.objects.filter(commit__commit_hash='0000100001000010000100001000010000100001').first()
        self.assertEqual(self.git_project1.id, trail1.project.id)
        self.assertEqual('master', trail1.branch.name)
        self.assertEqual('0000100001000010000100001000010000100001', trail1.commit.commit_hash)

        trail2 = GitBranchTrailEntry.objects.filter(commit__commit_hash='0000200002000020000200002000020000200002').first()
        self.assertEqual(self.git_project1.id, trail2.project.id)
        self.assertEqual('master', trail2.branch.name)
        self.assertEqual('0000200002000020000200002000020000200002', trail2.commit.commit_hash)

        merge_target_1 = GitBranchMergeTargetEntry.objects.filter(current_branch__name='master').first()
        self.assertEqual(self.git_project1.id, merge_target_1.project.id)
        self.assertEqual('master', merge_target_1.current_branch.name)
        self.assertEqual('master', merge_target_1.target_branch.name)
        self.assertEqual('merge-target-content', merge_target_1.diff.content)
        self.assertEqual('0000200002000020000200002000020000200002', merge_target_1.diff.commit_son.commit_hash)
        self.assertEqual('0000200002000020000200002000020000200002', merge_target_1.diff.commit_parent.commit_hash)


    def test_branch_trails(self):
        commit_time = str(timezone.now().isoformat())
        commit1 = FeederTestHelper.create_commit(1, [], 'user1', 'user1@test.com', commit_time, commit_time)
        commit2 = FeederTestHelper.create_commit(2, [1], 'user1', 'user1@test.com', commit_time, commit_time)
        commit3 = FeederTestHelper.create_commit(3, [2], 'user1', 'user1@test.com', commit_time, commit_time)

        branch1 = FeederTestHelper.create_branch('master', 3, 'master', 3, 1, [3, 2, 1], 'merge-target-content')

        feed_data = {}
        feed_data['commits'] = []
        feed_data['commits'].append(commit1)
        feed_data['commits'].append(commit2)
        feed_data['commits'].append(commit3)
        feed_data['branches'] = []
        feed_data['branches'].append(branch1)
        feed_data['diffs'] = []
        feed_data['diffs'].append(FeederTestHelper.create_diff(1, 1, 'diff-1'))
        feed_data['diffs'].append(FeederTestHelper.create_diff(2, 1, 'diff-2-1'))
        feed_data['diffs'].append(FeederTestHelper.create_diff(3, 2, 'diff-3-2'))

        post_data = FeederTestHelper.create_feed_data_and_report(
            feed_data,
            FeederTestHelper.get_default_report(1)
        )

        resp = self.client.post(
            '/main/feed/commit/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(post_data),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual(3, GitCommitEntry.objects.all().count())
        self.assertEqual(2, GitParentEntry.objects.all().count())
        self.assertEqual(1, GitBranchEntry.objects.all().count())
        self.assertEqual(3, GitBranchTrailEntry.objects.all().count())

        self.assertIsNotNone(GitCommitEntry.objects.filter(commit_hash='0000100001000010000100001000010000100001').first())
        self.assertIsNotNone(GitCommitEntry.objects.filter(commit_hash='0000200002000020000200002000020000200002').first())
        self.assertIsNotNone(GitCommitEntry.objects.filter(commit_hash='0000300003000030000300003000030000300003').first())

        self.assertIsNotNone(GitParentEntry.objects.filter(parent__commit_hash='0000100001000010000100001000010000100001').first())
        self.assertIsNotNone(GitParentEntry.objects.filter(parent__commit_hash='0000200002000020000200002000020000200002').first())

        self.assertIsNotNone(GitBranchEntry.objects.filter(name='master').first())

        self.assertIsNotNone(GitBranchTrailEntry.objects.filter(commit__commit_hash='0000100001000010000100001000010000100001').first())
        self.assertIsNotNone(0, GitBranchTrailEntry.objects.filter(commit__commit_hash='0000100001000010000100001000010000100001').first().order)

        self.assertIsNotNone(GitBranchTrailEntry.objects.filter(commit__commit_hash='0000200002000020000200002000020000200002').first())
        self.assertIsNotNone(1, GitBranchTrailEntry.objects.filter(commit__commit_hash='0000200002000020000200002000020000200002').first().order)

        self.assertIsNotNone(GitBranchTrailEntry.objects.filter(commit__commit_hash='0000300003000030000300003000030000300003').first())
        self.assertIsNotNone(2, GitBranchTrailEntry.objects.filter(commit__commit_hash='0000300003000030000300003000030000300003').first().order)
