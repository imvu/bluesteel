""" View Branch tests """

from django.test import TestCase
from django.test import Client
from django.conf import settings
from django.utils import timezone
from app.logic.httpcommon import res
from app.logic.gitrepo.models.GitProjectModel import GitProjectEntry
from app.logic.gitrepo.models.GitBranchModel import GitBranchEntry
from app.logic.gitrepo.models.GitBranchTrailModel import GitBranchTrailEntry
from app.logic.gitrepo.models.GitBranchMergeTargetModel import GitBranchMergeTargetEntry
from app.logic.gitrepo.models.GitCommitModel import GitCommitEntry
from app.logic.gitrepo.models.GitUserModel import GitUserEntry
from app.logic.gitrepo.models.GitDiffModel import GitDiffEntry
from datetime import timedelta
import json

class ViewsBranchTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.git_project1 = GitProjectEntry.objects.create(url='http://test/a/')

        self.git_user1 = GitUserEntry.objects.create(
            project=self.git_project1,
            name='user1',
            email='user1@test.com'
        )

        self.git_commit1 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000100001000010000100001000010000100001', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())

        self.git_branch1 = GitBranchEntry.objects.create(project=self.git_project1, name='branch-1', commit=self.git_commit1, order=0)
        self.git_branch2 = GitBranchEntry.objects.create(project=self.git_project1, name='branch-2', commit=self.git_commit1, order=1)
        self.git_branch3 = GitBranchEntry.objects.create(project=self.git_project1, name='branch-3', commit=self.git_commit1, order=2)
        self.git_branch4 = GitBranchEntry.objects.create(project=self.git_project1, name='branch-4', commit=self.git_commit1, order=3)
        self.git_branch5 = GitBranchEntry.objects.create(project=self.git_project1, name='branch-5', commit=self.git_commit1, order=4)

    def tearDown(self):
        pass

    def test_udpate_branch_1_order_value_to_be_the_last(self):
        resp = self.client.post(
            '/main/branch/{0}/project/{1}/update/order/28/'.format(self.git_branch1.id, self.git_project1.id),
            data = '{}',
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual(4, GitBranchEntry.objects.filter(id=self.git_branch1.id).first().order)
        self.assertEqual(0, GitBranchEntry.objects.filter(id=self.git_branch2.id).first().order)
        self.assertEqual(1, GitBranchEntry.objects.filter(id=self.git_branch3.id).first().order)
        self.assertEqual(2, GitBranchEntry.objects.filter(id=self.git_branch4.id).first().order)
        self.assertEqual(3, GitBranchEntry.objects.filter(id=self.git_branch5.id).first().order)

    def test_udpate_branch_5_order_value_to_be_the_first(self):
        resp = self.client.post(
            '/main/branch/{0}/project/{1}/update/order/0/'.format(self.git_branch5.id, self.git_project1.id),
            data = '{}',
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual(1, GitBranchEntry.objects.filter(id=self.git_branch1.id).first().order)
        self.assertEqual(2, GitBranchEntry.objects.filter(id=self.git_branch2.id).first().order)
        self.assertEqual(3, GitBranchEntry.objects.filter(id=self.git_branch3.id).first().order)
        self.assertEqual(4, GitBranchEntry.objects.filter(id=self.git_branch4.id).first().order)
        self.assertEqual(0, GitBranchEntry.objects.filter(id=self.git_branch5.id).first().order)

    def test_udpate_branch_5_order_value_to_be_the_third(self):
        resp = self.client.post(
            '/main/branch/{0}/project/{1}/update/order/2/'.format(self.git_branch5.id, self.git_project1.id),
            data = '{}',
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual(0, GitBranchEntry.objects.filter(id=self.git_branch1.id).first().order)
        self.assertEqual(1, GitBranchEntry.objects.filter(id=self.git_branch2.id).first().order)
        self.assertEqual(3, GitBranchEntry.objects.filter(id=self.git_branch3.id).first().order)
        self.assertEqual(4, GitBranchEntry.objects.filter(id=self.git_branch4.id).first().order)
        self.assertEqual(2, GitBranchEntry.objects.filter(id=self.git_branch5.id).first().order)
