""" BenchmarkExecution Views tests """

from django.test import TestCase
from django.test import Client
from django.utils import timezone
from app.service.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.service.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.service.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.service.gitrepo.models.GitProjectModel import GitProjectEntry
from app.service.gitrepo.models.GitUserModel import GitUserEntry
from app.service.gitrepo.models.GitCommitModel import GitCommitEntry
from app.util.commandrepo.models.CommandGroupModel import CommandGroupEntry
from app.util.commandrepo.models.CommandSetModel import CommandSetEntry
from app.util.commandrepo.models.CommandModel import CommandEntry
from app.util.httpcommon import res
import json

class BenchmarkViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()

        self.git_project1 = GitProjectEntry.objects.create(url='http://test/')

        self.git_user1 = GitUserEntry.objects.create(
            project=self.git_project1,
            name='user1',
            email='user1@test.com'
        )

        self.commit1 = GitCommitEntry.objects.create(
            project=self.git_project1,
            commit_hash='0000100001000010000100001000010000100001',
            author=self.git_user1,
            author_date=timezone.now(),
            committer=self.git_user1,
            committer_date=timezone.now()
        )

        self.commit2 = GitCommitEntry.objects.create(
            project=self.git_project1,
            commit_hash='0000200002000020000200002000020000200002',
            author=self.git_user1,
            author_date=timezone.now(),
            committer=self.git_user1,
            committer_date=timezone.now()
        )

        self.commit3 = GitCommitEntry.objects.create(
            project=self.git_project1,
            commit_hash='0000300003000030000300003000030000300003',
            author=self.git_user1,
            author_date=timezone.now(),
            committer=self.git_user1,
            committer_date=timezone.now()
        )

        self.command_group = CommandGroupEntry.objects.create()
        self.command_set = CommandSetEntry.objects.create(
            group=self.command_group
        )

        self.bluesteel_layout = BluesteelLayoutEntry.objects.create(
            name='Layout',
            active=True,
            project_index_path=0,
        )

        self.bluesteel_project = BluesteelProjectEntry.objects.create(
            name='Project',
            order=0,
            layout=self.bluesteel_layout,
            command_group=self.command_group,
            git_project=self.git_project1,
        )

    def tearDown(self):
        pass

    def test_acqiere_execution_is_none_because_no_definition(self):
        resp = self.client.post('/main/execution/acquire/')

        resp = self.client.post(
            '/main/execution/acquire/',
            data = json.dumps({}),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(404, resp_obj['status'])
        self.assertEqual('Next Execution not found', resp_obj['message'])


    def test_three_executions_acqiered_with_one_definition(self):
        benchmark_definition = BenchmarkDefinitionEntry.objects.create(
            name='BenchmarkDefinition',
            layout=self.bluesteel_layout,
            project=self.bluesteel_project,
            command_set=self.command_set,
        )

        # First
        resp = self.client.post(
            '/main/execution/acquire/',
            data = json.dumps({}),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual(1, resp_obj['data']['status']['index'])
        self.assertEqual('In_Progress', resp_obj['data']['status']['name'])
        self.assertEqual('0000300003000030000300003000030000300003', resp_obj['data']['commit'])
        self.assertEqual(False, resp_obj['data']['invalidated'])

        # Second
        resp = self.client.post(
            '/main/execution/acquire/',
            data = json.dumps({}),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual(1, resp_obj['data']['status']['index'])
        self.assertEqual('In_Progress', resp_obj['data']['status']['name'])
        self.assertEqual('0000200002000020000200002000020000200002', resp_obj['data']['commit'])
        self.assertEqual(False, resp_obj['data']['invalidated'])

        # Third
        resp = self.client.post(
            '/main/execution/acquire/',
            data = json.dumps({}),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual(1, resp_obj['data']['status']['index'])
        self.assertEqual('In_Progress', resp_obj['data']['status']['name'])
        self.assertEqual('0000100001000010000100001000010000100001', resp_obj['data']['commit'])
        self.assertEqual(False, resp_obj['data']['invalidated'])

        # Nothing else
        resp = self.client.post(
            '/main/execution/acquire/',
            data = json.dumps({}),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(404, resp_obj['status'])

