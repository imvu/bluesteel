""" View BranchMergeTarget tests """

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

class ViewsGitMergeTargetTestCase(TestCase):

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

        self.git_diff1 = GitDiffEntry.objects.create(
            project=self.git_project1,
            commit_son=self.git_commit1,
            commit_parent=self.git_commit3,
            content='diff-1-3'
        )

        self.git_merge_target1 = GitBranchMergeTargetEntry.objects.create(
            project=self.git_project1,
            current_branch=self.git_branch1,
            target_branch=self.git_branch1,
            diff=self.git_diff1
        )

    def tearDown(self):
        pass

    def test_project_not_found(self):
        resp = self.client.post(
            '/git/branch/merge/target/project/128/',
            data = '{}',
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(404, resp_obj['status'])
        self.assertEqual('project not found', resp_obj['message'])

    def test_json_data_is_incorrect(self):
        resp = self.client.post(
            '/git/branch/merge/target/project/{0}/'.format(self.git_project1.id),
            data = '/',
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(406, resp_obj['status'])
        self.assertEqual('Json parser failed.', resp_obj['message'])

    def test_schema_is_incorrect_because_current_name_too_short(self):
        obj = {}
        obj['current_branch_name'] = ''
        obj['target_branch_name'] = 'name'

        resp = self.client.post(
            '/git/branch/merge/target/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(obj),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(406, resp_obj['status'])
        self.assertEqual('Schema failed.', resp_obj['message'])

    def test_current_branch_not_found(self):
        obj = {}
        obj['current_branch_name'] = 'branch-5'
        obj['target_branch_name'] = 'branch-3'

        resp = self.client.post(
            '/git/branch/merge/target/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(obj),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(404, resp_obj['status'])
        self.assertEqual('Current branch name not found', resp_obj['message'])

    def test_target_branch_not_found(self):
        obj = {}
        obj['current_branch_name'] = 'branch-1'
        obj['target_branch_name'] = 'branch-5'

        resp = self.client.post(
            '/git/branch/merge/target/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(obj),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(404, resp_obj['status'])
        self.assertEqual('Target branch name not found', resp_obj['message'])

    def test_merge_target_not_found(self):
        obj = {}
        obj['current_branch_name'] = 'branch-3'
        obj['target_branch_name'] = 'branch-3'

        resp = self.client.post(
            '/git/branch/merge/target/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(obj),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(404, resp_obj['status'])
        self.assertEqual('Merge Target entry not found', resp_obj['message'])

    def test_merge_target_changed_and_invalidated(self):
        self.assertEqual('branch-1', self.git_merge_target1.target_branch.name)
        self.assertEqual(False, self.git_merge_target1.invalidated)

        obj = {}
        obj['current_branch_name'] = 'branch-1'
        obj['target_branch_name'] = 'branch-3'

        resp = self.client.post(
            '/git/branch/merge/target/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(obj),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual('Target branch changed', resp_obj['message'])
        self.assertEqual(True, GitBranchMergeTargetEntry.objects.get(project=self.git_project1, target_branch=self.git_branch3).invalidated)
        self.assertEqual('branch-3', GitBranchMergeTargetEntry.objects.get(project=self.git_project1, target_branch=self.git_branch3).target_branch.name)

    def test_merge_target_not_changed_because_its_the_same(self):
        self.git_merge_target1.target_branch = self.git_branch3
        self.git_merge_target1.save()

        self.assertEqual('branch-3', self.git_merge_target1.target_branch.name)
        self.assertEqual(False, self.git_merge_target1.invalidated)

        obj = {}
        obj['current_branch_name'] = 'branch-1'
        obj['target_branch_name'] = 'branch-3'

        resp = self.client.post(
            '/git/branch/merge/target/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(obj),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual('Target branch not changed', resp_obj['message'])
        self.assertEqual(False, GitBranchMergeTargetEntry.objects.get(project=self.git_project1, target_branch=self.git_branch3).invalidated)
        self.assertEqual('branch-3', GitBranchMergeTargetEntry.objects.get(project=self.git_project1, target_branch=self.git_branch3).target_branch.name)
