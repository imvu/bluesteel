""" Git Feed Views branch tests """

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

        merge_target = FeederTestHelper.create_merge_target('master', FeederTestHelper.hash_string(2), FeederTestHelper.hash_string(2), 'merge-target-content')

        branch1 = FeederTestHelper.create_branch('master', 2, [FeederTestHelper.hash_string(2)], merge_target)

        post_data = {}
        post_data['commits'] = []
        post_data['commits'].append(commit1)
        post_data['branches'] = []
        post_data['branches'].append(branch1)
        post_data['diffs'] = []

        resp = self.client.post(
            '/gitfeeder/feed/commit/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(post_data),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(400, resp_obj['status'])
        self.assertEqual('Branches not correct', resp_obj['message'])
        self.assertEqual(0, GitCommitEntry.objects.all().count())
        self.assertEqual(0, GitBranchEntry.objects.all().count())


    def test_branch_trails(self):
        commit_time = str(timezone.now().isoformat())
        commit1 = FeederTestHelper.create_commit(1, [], 'user1', 'user1@test.com', commit_time, commit_time)
        commit2 = FeederTestHelper.create_commit(2, [FeederTestHelper.hash_string(1)], 'user1', 'user1@test.com', commit_time, commit_time)
        commit3 = FeederTestHelper.create_commit(3, [FeederTestHelper.hash_string(2)], 'user1', 'user1@test.com', commit_time, commit_time)

        merge_target = FeederTestHelper.create_merge_target('master', FeederTestHelper.hash_string(3), FeederTestHelper.hash_string(3), 'merge-target-content')

        branch1 = FeederTestHelper.create_branch('master', 3, [FeederTestHelper.hash_string(3), FeederTestHelper.hash_string(2), FeederTestHelper.hash_string(1)], merge_target)

        post_data = {}
        post_data['commits'] = []
        post_data['commits'].append(commit1)
        post_data['commits'].append(commit2)
        post_data['commits'].append(commit3)
        post_data['branches'] = []
        post_data['branches'].append(branch1)
        post_data['diffs'] = []

        resp = self.client.post(
            '/gitfeeder/feed/commit/project/{0}/'.format(self.git_project1.id),
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
        self.assertIsNotNone(GitBranchTrailEntry.objects.filter(commit__commit_hash='0000200002000020000200002000020000200002').first())
        self.assertIsNotNone(GitBranchTrailEntry.objects.filter(commit__commit_hash='0000300003000030000300003000030000300003').first())