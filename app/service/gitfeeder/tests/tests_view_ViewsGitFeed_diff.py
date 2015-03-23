""" Git Feed Views diff tests """

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

class GitFeedViewsDiffTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.git_project1 = GitProjectEntry.objects.create(url='http://test/')
        self.git_user1 = GitUserEntry.objects.create(
            project=self.git_project1,
            name='user1',
            email='user1@test.com'
        )

        self.commit_time = str(timezone.now().isoformat())
        self.commit1 = FeederTestHelper.create_commit(1, [], 'user1', 'user1@test.com', self.commit_time, self.commit_time)
        self.commit2 = FeederTestHelper.create_commit(2, [], 'user1', 'user1@test.com', self.commit_time, self.commit_time)

        self.merge_target = FeederTestHelper.create_merge_target('master', FeederTestHelper.hash_string(1), FeederTestHelper.hash_string(1), 'merge-target-content')

        self.branch1 = FeederTestHelper.create_branch('master', 1, [FeederTestHelper.hash_string(1)], self.merge_target)

    def tearDown(self):
        pass


    def test_two_commits_one_diff(self):
        post_data = {}
        post_data['commits'] = []
        post_data['commits'].append(self.commit1)
        post_data['commits'].append(self.commit2)
        post_data['branches'] = []
        post_data['branches'].append(self.branch1)
        post_data['diffs'] = []
        post_data['diffs'].append(FeederTestHelper.create_diff(FeederTestHelper.hash_string(1), FeederTestHelper.hash_string(1), 'diff-1'))
        post_data['diffs'].append(FeederTestHelper.create_diff(self.commit2['commit_hash'], self.commit1['commit_hash'], 'diff-2-1'))

        resp = self.client.post(
            '/gitfeeder/feed/commit/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(post_data),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual(2, GitCommitEntry.objects.all().count())
        self.assertEqual(1, GitBranchEntry.objects.all().count())
        self.assertEqual(3, GitDiffEntry.objects.all().count())

        diff_entry1 = GitDiffEntry.objects.filter(
            project=self.git_project1,
            commit_son__commit_hash='0000100001000010000100001000010000100001',
            commit_parent__commit_hash='0000100001000010000100001000010000100001'
        ).first()
        self.assertEqual('diff-1', diff_entry1.content)

        diff_entry2 = GitDiffEntry.objects.filter(
            project=self.git_project1,
            commit_son__commit_hash='0000200002000020000200002000020000200002',
            commit_parent__commit_hash='0000100001000010000100001000010000100001'
        ).first()
        self.assertEqual('diff-2-1', diff_entry2.content)


        branch_entry = GitBranchEntry.objects.all().first()
        self.assertEqual('0000100001000010000100001000010000100001', branch_entry.commit.commit_hash)
        self.assertEqual('master', branch_entry.name)

    def test_incorrect_diff_because_son_not_present(self):
        post_data = {}
        post_data['commits'] = []
        post_data['commits'].append(self.commit1)
        post_data['commits'].append(self.commit2)
        post_data['branches'] = []
        post_data['branches'].append(self.branch1)
        post_data['diffs'] = []
        post_data['diffs'].append(FeederTestHelper.create_diff(FeederTestHelper.hash_string(1), FeederTestHelper.hash_string(1), 'diff-1'))
        post_data['diffs'].append(FeederTestHelper.create_diff('0000300003000030000300003000030000300003', self.commit2['commit_hash'], 'diff-3-2'))

        resp = self.client.post(
            '/gitfeeder/feed/commit/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(post_data),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(400, resp_obj['status'])
        self.assertEqual('Diffs not correct', resp_obj['message'])
        self.assertEqual(0, GitCommitEntry.objects.all().count())
        self.assertEqual(0, GitBranchEntry.objects.all().count())

    def test_incorrect_diff_because_parent_not_present(self):
        post_data = {}
        post_data['commits'] = []
        post_data['commits'].append(self.commit1)
        post_data['commits'].append(self.commit2)
        post_data['branches'] = []
        post_data['branches'].append(self.branch1)
        post_data['diffs'] = []
        post_data['diffs'].append(FeederTestHelper.create_diff(FeederTestHelper.hash_string(1), FeederTestHelper.hash_string(1), 'diff-1'))
        post_data['diffs'].append(FeederTestHelper.create_diff('0000200002000020000200002000020000200002', FeederTestHelper.hash_string(0), 'diff-3-2'))

        resp = self.client.post(
            '/gitfeeder/feed/commit/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(post_data),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(400, resp_obj['status'])
        self.assertEqual('Diffs not correct', resp_obj['message'])
        self.assertEqual(0, GitCommitEntry.objects.all().count())
        self.assertEqual(0, GitBranchEntry.objects.all().count())

    def test_incorrect_diff_because_not_diff_present(self):
        post_data = {}
        post_data['commits'] = []
        post_data['commits'].append(self.commit1)
        post_data['commits'].append(self.commit2)
        post_data['branches'] = []
        post_data['branches'].append(self.branch1)
        post_data['diffs'] = []
        post_data['diffs'].append(FeederTestHelper.create_diff(FeederTestHelper.hash_string(1), FeederTestHelper.hash_string(1), 'diff-1'))

        resp = self.client.post(
            '/gitfeeder/feed/commit/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(post_data),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(400, resp_obj['status'])
        self.assertEqual('Diffs not correct', resp_obj['message'])
        self.assertEqual(0, GitCommitEntry.objects.all().count())
        self.assertEqual(0, GitBranchEntry.objects.all().count())