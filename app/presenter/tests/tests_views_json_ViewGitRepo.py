""" View git repo tests """

from django.test import TestCase
from django.test import Client
from django.conf import settings
from django.utils import timezone
from app.util.httpcommon import res
from app.service.gitrepo.models.GitProjectModel import GitProjectEntry
from app.service.gitrepo.models.GitBranchModel import GitBranchEntry
from app.service.gitrepo.models.GitBranchMergeTargetModel import GitBranchMergeTargetEntry
from app.service.gitrepo.models.GitCommitModel import GitCommitEntry
from app.service.gitrepo.models.GitUserModel import GitUserEntry
from app.service.gitrepo.models.GitDiffModel import GitDiffEntry
from datetime import timedelta
import json

# Create your tests here.

class ViewsGitRepoTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.git_project1 = GitProjectEntry.objects.create(url='http://test/a/')
        self.git_project2 = GitProjectEntry.objects.create(url='http://test/b/')

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
            project=self.git_project2,
            commit_hash='0000200002000020000200002000020000200002',
            author=self.git_user1,
            author_date=timezone.now(),
            committer=self.git_user1,
            committer_date=timezone.now()
        )

        self.git_commit3 = GitCommitEntry.objects.create(
            project=self.git_project1,
            commit_hash='0000300003000030000300003000030000300003',
            author=self.git_user1,
            author_date=timezone.now(),
            committer=self.git_user1,
            committer_date=timezone.now()
        )

        self.git_branch1 = GitBranchEntry.objects.create(
            project=self.git_project1,
            name='branch-1',
            commit=self.git_commit1)

        self.git_branch2 = GitBranchEntry.objects.create(
            project=self.git_project2,
            name='branch-2',
            commit=self.git_commit2)

        self.git_branch3 = GitBranchEntry.objects.create(
            project=self.git_project1,
            name='branch-3',
            commit=self.git_commit3)

    def tearDown(self):
        pass

    def test_get_all_branches_of_a_project(self):
        resp = self.client.get('/main/branch/all/project/{0}/'.format(self.git_project1.id))

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(2, len(resp_obj['data']))
        self.assertEqual('branch-1', resp_obj['data'][0]['name'])
        self.assertEqual('0000100001000010000100001000010000100001', resp_obj['data'][0]['commit_hash'])
        self.assertFalse('target_branch_name' in resp_obj['data'][0])

        self.assertEqual('branch-3', resp_obj['data'][1]['name'])
        self.assertEqual('0000300003000030000300003000030000300003', resp_obj['data'][1]['commit_hash'])
        self.assertFalse('target_branch_name' in resp_obj['data'][1])

    def test_get_all_branches_and_merge_target_info(self):
        diff_entry = GitDiffEntry.objects.create(
            project=self.git_project1,
            commit_son=self.git_commit3,
            commit_parent=self.git_commit1,
            content='diff-3-1'
        )

        GitBranchMergeTargetEntry.objects.create(
            project=self.git_project1,
            current_branch=self.git_branch3,
            target_branch=self.git_branch1,
            fork_point=self.git_commit1,
            diff=diff_entry
        )

        resp = self.client.get('/main/branch/all/project/{0}/'.format(self.git_project1.id))

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(2, len(resp_obj['data']))
        self.assertEqual('branch-1', resp_obj['data'][0]['name'])
        self.assertEqual('0000100001000010000100001000010000100001', resp_obj['data'][0]['commit_hash'])
        self.assertFalse('target_branch_name' in resp_obj['data'][0])

        self.assertEqual('branch-3', resp_obj['data'][1]['name'])
        self.assertEqual('0000300003000030000300003000030000300003', resp_obj['data'][1]['commit_hash'])
        self.assertEqual('branch-1', resp_obj['data'][1]['target_branch_name'])
