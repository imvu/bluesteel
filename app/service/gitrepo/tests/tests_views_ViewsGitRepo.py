""" View git repo tests """

from django.test import TestCase
from django.test import Client
from django.conf import settings
from django.utils import timezone
from app.util.httpcommon import res
from app.service.gitrepo.models.GitProjectModel import GitProjectEntry
from app.service.gitrepo.models.GitBranchModel import GitBranchEntry
from app.service.gitrepo.models.GitHashModel import GitHashEntry
from datetime import timedelta
import json

# Create your tests here.

class ViewsGitRepoTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.git_project1 = GitProjectEntry.objects.create(url='http://test/a/')
        self.git_project2 = GitProjectEntry.objects.create(url='http://test/b/')

        self.git_hash1 = GitHashEntry.objects.create(
            project=self.git_project1,
            git_hash='0000100001000010000100001000010000100001'
        )

        self.git_hash2 = GitHashEntry.objects.create(
            project=self.git_project2,
            git_hash='0000200002000020000200002000020000200002'
        )

        self.git_hash3 = GitHashEntry.objects.create(
            project=self.git_project1,
            git_hash='0000300003000030000300003000030000300003'
        )

        self.git_branch1 = GitBranchEntry.objects.create(
            project=self.git_project1,
            name='branch-1',
            commit_hash=self.git_hash1)

        self.git_branch2 = GitBranchEntry.objects.create(
            project=self.git_project2,
            name='branch-2',
            commit_hash=self.git_hash2)

        self.git_branch3 = GitBranchEntry.objects.create(
            project=self.git_project1,
            name='branch-3',
            commit_hash=self.git_hash3)

    def tearDown(self):
        pass

    def test_get_all_branches_of_a_project(self):
        resp = self.client.get('/git/branch/all/project/{0}/'.format(self.git_project1.id))

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(2, len(resp_obj['data']))
        self.assertEqual('branch-1', resp_obj['data'][0]['name'])
        self.assertEqual('branch-3', resp_obj['data'][1]['name'])
