""" Git Feed Views commit tests """

from django.test import TestCase
from django.test import Client
from django.conf import settings
from django.utils import timezone
from app.service.gitrepo.models.GitProjectModel import GitProjectEntry
from app.service.gitrepo.models.GitUserModel import GitUserEntry
from app.service.gitrepo.models.GitCommitModel import GitCommitEntry
from app.service.gitrepo.models.GitParentModel import GitParentEntry
from app.service.gitrepo.models.GitDiffModel import GitDiffEntry
from app.service.gitrepo.models.GitBranchModel import GitBranchEntry
from app.service.gitrepo.models.GitBranchTrailModel import GitBranchTrailEntry
from app.service.gitfeeder.helper import FeederTestHelper
from app.util.httpcommon import res
from datetime import timedelta
import json
import os
import hashlib
import shutil

# Create your tests here.

class GitFeedViewsCommitTestCase(TestCase):

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

    def test_feed_simple_commit(self):
        commit_time = str(timezone.now().isoformat())
        commit1 = FeederTestHelper.create_commit(1, [], 'user1', 'user1@test.com', commit_time, commit_time)

        merge_target = FeederTestHelper.create_merge_target(
            'master',
            FeederTestHelper.hash_string(1),
            'master',
            FeederTestHelper.hash_string(1),
            FeederTestHelper.hash_string(1),
            'merge-target-content'
        )

        branch1 = FeederTestHelper.create_branch('master', 1, [FeederTestHelper.hash_string(1)], merge_target)

        feed_data = {}
        feed_data['commits'] = []
        feed_data['commits'].append(commit1)
        feed_data['branches'] = []
        feed_data['branches'].append(branch1)
        feed_data['diffs'] = []
        feed_data['diffs'].append(FeederTestHelper.create_diff(FeederTestHelper.hash_string(1), FeederTestHelper.hash_string(1), 'diff-1'))

        post_data = FeederTestHelper.create_feed_data_and_report(
            feed_data,
            FeederTestHelper.get_default_report()
        )

        resp = self.client.post(
            '/gitfeeder/feed/commit/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(post_data),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual(1, GitCommitEntry.objects.all().count())
        self.assertEqual(1, GitBranchEntry.objects.all().count())

        branch_entry = GitBranchEntry.objects.all().first()
        self.assertEqual('0000100001000010000100001000010000100001', branch_entry.commit.commit_hash)
        self.assertEqual('master', branch_entry.name)


    def test_feed_simple_commit_already_present(self):
        git_commit1 = GitCommitEntry.objects.create(
            project=self.git_project1,
            commit_hash='0000100001000010000100001000010000100001',
            author=self.git_user1,
            author_date=timezone.now(),
            committer=self.git_user1,
            committer_date=timezone.now()
        )

        commit_time = str(timezone.now().isoformat())
        commit1 = FeederTestHelper.create_commit(1, [], 'user1', 'user1@test.com', commit_time, commit_time)

        merge_target = FeederTestHelper.create_merge_target(
            'master',
            FeederTestHelper.hash_string(1),
            'master',
            FeederTestHelper.hash_string(1),
            FeederTestHelper.hash_string(1),
            'merge-target-content'
        )

        branch1 = FeederTestHelper.create_branch('master', 1, [FeederTestHelper.hash_string(1)], merge_target)

        feed_data = {}
        feed_data['commits'] = []
        feed_data['commits'].append(commit1)
        feed_data['branches'] = []
        feed_data['branches'].append(branch1)
        feed_data['diffs'] = []
        feed_data['diffs'].append(FeederTestHelper.create_diff(FeederTestHelper.hash_string(1), FeederTestHelper.hash_string(1), 'diff-1'))

        post_data = FeederTestHelper.create_feed_data_and_report(
            feed_data,
            FeederTestHelper.get_default_report()
        )

        resp = self.client.post(
            '/gitfeeder/feed/commit/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(post_data),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual(1, GitCommitEntry.objects.all().count())
        self.assertEqual(1, GitBranchEntry.objects.all().count())

        branch_entry = GitBranchEntry.objects.all().first()
        self.assertEqual('0000100001000010000100001000010000100001', branch_entry.commit.commit_hash)
        self.assertEqual('master', branch_entry.name)


    def test_feed_fail_because_commits_are_not_unique(self):
        commit_time = str(timezone.now().isoformat())
        commit1 = FeederTestHelper.create_commit(1, [], 'user1', 'user1@test.com', commit_time, commit_time)
        commit2 = FeederTestHelper.create_commit(1, [], 'user1', 'user1@test.com', commit_time, commit_time)
        commit3 = FeederTestHelper.create_commit(2, [], 'user1', 'user1@test.com', commit_time, commit_time)
        commit4 = FeederTestHelper.create_commit(3, [], 'user1', 'user1@test.com', commit_time, commit_time)

        merge_target = FeederTestHelper.create_merge_target(
            'master',
            FeederTestHelper.hash_string(3),
            'master',
            FeederTestHelper.hash_string(3),
            FeederTestHelper.hash_string(3),
            'merge-target-content'
        )

        branch1 = FeederTestHelper.create_branch('master', 1, [FeederTestHelper.hash_string(1)], merge_target)

        feed_data = {}
        feed_data['commits'] = []
        feed_data['commits'].append(commit1)
        feed_data['commits'].append(commit2)
        feed_data['commits'].append(commit3)
        feed_data['commits'].append(commit4)
        feed_data['branches'] = []
        feed_data['branches'].append(branch1)
        feed_data['diffs'] = []
        feed_data['diffs'].append(FeederTestHelper.create_diff(FeederTestHelper.hash_string(1), FeederTestHelper.hash_string(1), 'diff-1'))
        feed_data['diffs'].append(FeederTestHelper.create_diff(FeederTestHelper.hash_string(2), FeederTestHelper.hash_string(1), 'diff-2-1'))
        feed_data['diffs'].append(FeederTestHelper.create_diff(FeederTestHelper.hash_string(3), FeederTestHelper.hash_string(2), 'diff-3-2'))

        post_data = FeederTestHelper.create_feed_data_and_report(
            feed_data,
            FeederTestHelper.get_default_report()
        )

        resp = self.client.post(
            '/gitfeeder/feed/commit/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(post_data),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(400, resp_obj['status'])
        self.assertEqual('Commits not unique', resp_obj['message'])
        self.assertEqual(0, GitCommitEntry.objects.all().count())
        self.assertEqual(0, GitBranchEntry.objects.all().count())


    def test_two_commits_one_parent(self):
        commit_time = str(timezone.now().isoformat())
        commit1 = FeederTestHelper.create_commit(1, [], 'user1', 'user1@test.com', commit_time, commit_time)
        commit2 = FeederTestHelper.create_commit(2, [], 'user1', 'user1@test.com', commit_time, commit_time)

        commit1['parent_hashes'].append(commit2['hash'])

        merge_target = FeederTestHelper.create_merge_target(
            'master',
            FeederTestHelper.hash_string(1),
            'master',
            FeederTestHelper.hash_string(1),
            FeederTestHelper.hash_string(1),
            'merge-target-content'
        )

        branch1 = FeederTestHelper.create_branch('master', 1, [FeederTestHelper.hash_string(1)], merge_target)

        feed_data = {}
        feed_data['commits'] = []
        feed_data['commits'].append(commit1)
        feed_data['commits'].append(commit2)
        feed_data['branches'] = []
        feed_data['branches'].append(branch1)
        feed_data['diffs'] = []
        feed_data['diffs'].append(FeederTestHelper.create_diff(FeederTestHelper.hash_string(1), FeederTestHelper.hash_string(1), 'diff-1'))
        feed_data['diffs'].append(FeederTestHelper.create_diff(FeederTestHelper.hash_string(2), FeederTestHelper.hash_string(1), 'diff-2-1'))

        post_data = FeederTestHelper.create_feed_data_and_report(
            feed_data,
            FeederTestHelper.get_default_report()
        )

        resp = self.client.post(
            '/gitfeeder/feed/commit/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(post_data),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual(2, GitCommitEntry.objects.all().count())
        self.assertEqual(1, GitParentEntry.objects.all().count())
        self.assertEqual(1, GitBranchEntry.objects.all().count())

        parent_entry = GitParentEntry.objects.all().first()
        self.assertEqual('0000200002000020000200002000020000200002', parent_entry.parent.commit_hash)
        self.assertEqual('0000100001000010000100001000010000100001', parent_entry.son.commit_hash)

        branch_entry = GitBranchEntry.objects.all().first()
        self.assertEqual('0000100001000010000100001000010000100001', branch_entry.commit.commit_hash)
        self.assertEqual('master', branch_entry.name)


    def test_feed_fails_because_bad_constructed_parent(self):
        commit_time = str(timezone.now().isoformat())
        commit1 = FeederTestHelper.create_commit(1, [], 'user1', 'user1@test.com', commit_time, commit_time)
        commit2 = FeederTestHelper.create_commit(2, [FeederTestHelper.hash_string(3)], 'user1', 'user1@test.com', commit_time, commit_time)

        merge_target = FeederTestHelper.create_merge_target(
            'master',
            FeederTestHelper.hash_string(2),
            'master',
            FeederTestHelper.hash_string(2),
            FeederTestHelper.hash_string(2),
            'merge-target-content'
        )

        branch1 = FeederTestHelper.create_branch('master', 2, [FeederTestHelper.hash_string(2), FeederTestHelper.hash_string(1)], merge_target)

        feed_data = {}
        feed_data['commits'] = []
        feed_data['commits'].append(commit1)
        feed_data['commits'].append(commit2)
        feed_data['branches'] = []
        feed_data['branches'].append(branch1)
        feed_data['diffs'] = []
        feed_data['diffs'].append(FeederTestHelper.create_diff(FeederTestHelper.hash_string(1), FeederTestHelper.hash_string(1), 'diff-1'))
        feed_data['diffs'].append(FeederTestHelper.create_diff(FeederTestHelper.hash_string(2), FeederTestHelper.hash_string(1), 'diff-2-1'))

        post_data = FeederTestHelper.create_feed_data_and_report(
            feed_data,
            FeederTestHelper.get_default_report()
        )

        resp = self.client.post(
            '/gitfeeder/feed/commit/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(post_data),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(400, resp_obj['status'])
        self.assertEqual('Parents not correct', resp_obj['message'])


    def test_feed_two_times(self):
        commit_time = str(timezone.now().isoformat())
        commit1 = FeederTestHelper.create_commit(1, [], 'user1', 'user1@test.com', commit_time, commit_time)
        commit2 = FeederTestHelper.create_commit(2, [FeederTestHelper.hash_string(1)], 'user1', 'user1@test.com', commit_time, commit_time)
        commit3 = FeederTestHelper.create_commit(3, [FeederTestHelper.hash_string(1)], 'user1', 'user1@test.com', commit_time, commit_time)

        merge_target1 = FeederTestHelper.create_merge_target(
            'master',
            FeederTestHelper.hash_string(2),
            'master',
            FeederTestHelper.hash_string(2),
            FeederTestHelper.hash_string(1),
            'merge-target-content'
        )

        merge_target2 = FeederTestHelper.create_merge_target(
            'branch-1',
            FeederTestHelper.hash_string(3),
            'master',
            FeederTestHelper.hash_string(2),
            FeederTestHelper.hash_string(1),
            'merge-target-content-2'
        )

        branch1 = FeederTestHelper.create_branch('master', 2, [FeederTestHelper.hash_string(2), FeederTestHelper.hash_string(1)], merge_target1)
        branch2 = FeederTestHelper.create_branch('branch-1', 3, [FeederTestHelper.hash_string(3), FeederTestHelper.hash_string(1)], merge_target2)

        feed_data = {}
        feed_data['commits'] = []
        feed_data['commits'].append(commit1)
        feed_data['commits'].append(commit2)
        feed_data['commits'].append(commit3)
        feed_data['branches'] = []
        feed_data['branches'].append(branch1)
        feed_data['branches'].append(branch2)
        feed_data['diffs'] = []
        feed_data['diffs'].append(FeederTestHelper.create_diff(FeederTestHelper.hash_string(1), FeederTestHelper.hash_string(1), 'diff-1'))
        feed_data['diffs'].append(FeederTestHelper.create_diff(FeederTestHelper.hash_string(2), FeederTestHelper.hash_string(1), 'diff-2-1'))
        feed_data['diffs'].append(FeederTestHelper.create_diff(FeederTestHelper.hash_string(3), FeederTestHelper.hash_string(2), 'diff-3-2'))

        post_data = FeederTestHelper.create_feed_data_and_report(
            feed_data,
            FeederTestHelper.get_default_report()
        )

        resp = self.client.post(
            '/gitfeeder/feed/commit/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(post_data),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)
        self.assertEqual(200, resp_obj['status'])

        commit4 = FeederTestHelper.create_commit(4, [FeederTestHelper.hash_string(2)], 'user1', 'user1@test.com', commit_time, commit_time)
        commit5 = FeederTestHelper.create_commit(5, [FeederTestHelper.hash_string(3)], 'user1', 'user1@test.com', commit_time, commit_time)

        merge_target3 = FeederTestHelper.create_merge_target(
            'master',
            FeederTestHelper.hash_string(4),
            'master',
            FeederTestHelper.hash_string(4),
            FeederTestHelper.hash_string(1),
            'merge-target-content-3'
        )

        merge_target4 = FeederTestHelper.create_merge_target(
            'branch-1',
            FeederTestHelper.hash_string(5),
            'master',
            FeederTestHelper.hash_string(4),
            FeederTestHelper.hash_string(1),
            'merge-target-content-4'
        )

        branch1 = FeederTestHelper.create_branch('master', 4, [FeederTestHelper.hash_string(4), FeederTestHelper.hash_string(2), FeederTestHelper.hash_string(1)], merge_target3)
        branch2 = FeederTestHelper.create_branch('branch-1', 5, [FeederTestHelper.hash_string(5), FeederTestHelper.hash_string(3), FeederTestHelper.hash_string(1)], merge_target4)

        feed_data = {}
        feed_data['commits'] = []
        feed_data['commits'].append(commit4)
        feed_data['commits'].append(commit5)
        feed_data['branches'] = []
        feed_data['branches'].append(branch1)
        feed_data['branches'].append(branch2)
        feed_data['diffs'] = []
        feed_data['diffs'].append(FeederTestHelper.create_diff(FeederTestHelper.hash_string(4), FeederTestHelper.hash_string(3), 'diff-4-3'))
        feed_data['diffs'].append(FeederTestHelper.create_diff(FeederTestHelper.hash_string(5), FeederTestHelper.hash_string(4), 'diff-5-4'))

        post_data = FeederTestHelper.create_feed_data_and_report(
            feed_data,
            FeederTestHelper.get_default_report()
        )

        resp = self.client.post(
            '/gitfeeder/feed/commit/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(post_data),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)
        self.assertEqual(200, resp_obj['status'])

        self.assertEqual(5, GitCommitEntry.objects.all().count())
        self.assertEqual(4, GitParentEntry.objects.all().count())
        self.assertEqual(2, GitBranchEntry.objects.all().count())
        self.assertEqual(6, GitBranchTrailEntry.objects.all().count())

        self.assertIsNotNone(GitCommitEntry.objects.filter(commit_hash='0000100001000010000100001000010000100001').first())
        self.assertIsNotNone(GitCommitEntry.objects.filter(commit_hash='0000200002000020000200002000020000200002').first())
        self.assertIsNotNone(GitCommitEntry.objects.filter(commit_hash='0000300003000030000300003000030000300003').first())
        self.assertIsNotNone(GitCommitEntry.objects.filter(commit_hash='0000400004000040000400004000040000400004').first())
        self.assertIsNotNone(GitCommitEntry.objects.filter(commit_hash='0000500005000050000500005000050000500005').first())

        self.assertIsNotNone(GitParentEntry.objects.filter(parent__commit_hash='0000100001000010000100001000010000100001', son__commit_hash='0000200002000020000200002000020000200002').first())
        self.assertIsNotNone(GitParentEntry.objects.filter(parent__commit_hash='0000100001000010000100001000010000100001', son__commit_hash='0000300003000030000300003000030000300003').first())
        self.assertIsNotNone(GitParentEntry.objects.filter(parent__commit_hash='0000200002000020000200002000020000200002', son__commit_hash='0000400004000040000400004000040000400004').first())
        self.assertIsNotNone(GitParentEntry.objects.filter(parent__commit_hash='0000300003000030000300003000030000300003', son__commit_hash='0000500005000050000500005000050000500005').first())

        self.assertIsNotNone(GitBranchEntry.objects.filter(name='master').first())
        self.assertIsNotNone(GitBranchEntry.objects.filter(name='branch-1').first())

        self.assertIsNotNone(GitBranchTrailEntry.objects.filter(commit__commit_hash='0000100001000010000100001000010000100001', branch__name='master').first())
        self.assertIsNotNone(GitBranchTrailEntry.objects.filter(commit__commit_hash='0000200002000020000200002000020000200002', branch__name='master').first())
        self.assertIsNotNone(GitBranchTrailEntry.objects.filter(commit__commit_hash='0000400004000040000400004000040000400004', branch__name='master').first())
        self.assertIsNotNone(GitBranchTrailEntry.objects.filter(commit__commit_hash='0000100001000010000100001000010000100001', branch__name='branch-1').first())
        self.assertIsNotNone(GitBranchTrailEntry.objects.filter(commit__commit_hash='0000300003000030000300003000030000300003', branch__name='branch-1').first())
        self.assertIsNotNone(GitBranchTrailEntry.objects.filter(commit__commit_hash='0000500005000050000500005000050000500005', branch__name='branch-1').first())
