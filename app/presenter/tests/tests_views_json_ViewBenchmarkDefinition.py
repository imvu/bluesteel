""" Presenter Views BenchmarkDefinition tests """

from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from django.utils import timezone
from app.logic.benchmark.controllers.BenchmarkDefinitionController import BenchmarkDefinitionController
from app.logic.benchmark.controllers.BenchmarkExecutionController import BenchmarkExecutionController
from app.logic.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.logic.benchmark.models.BenchmarkExecutionModel import BenchmarkExecutionEntry
from app.logic.bluesteel.controllers.BluesteelLayoutController import BluesteelLayoutController
from app.logic.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.logic.gitrepo.models.GitProjectModel import GitProjectEntry
from app.logic.gitrepo.models.GitUserModel import GitUserEntry
from app.logic.gitrepo.models.GitCommitModel import GitCommitEntry
from app.logic.commandrepo.models.CommandSetModel import CommandSetEntry
from app.logic.commandrepo.models.CommandModel import CommandEntry
from app.logic.bluesteelworker.models.WorkerModel import WorkerEntry
from app.logic.httpcommon import res
import json

class BenchmarkDefinitionViewJsonTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user('user1@test.com', 'user1@test.com', 'pass')

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

        self.worker1 = WorkerEntry.objects.create(
            name='worker-name-1',
            uuid='uuid-worker-1',
            operative_system='osx',
            description='long-description-1',
            user=self.user1,
            git_feeder=False
        )

        self.worker2 = WorkerEntry.objects.create(
            name='worker-name-2',
            uuid='uuid-worker-2',
            operative_system='osx',
            description='long-description-2',
            user=self.user1,
            git_feeder=False
        )

    def tearDown(self):
        pass

    def test_create_benchmark_definition(self):
        layout = BluesteelLayoutController.create_new_default_layout()

        self.assertEqual(0, BenchmarkDefinitionEntry.objects.all().count())
        self.assertEqual(0, BenchmarkExecutionEntry.objects.all().count())

        resp = self.client.post(
            '/main/definitions/create/',
            data = '',
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])

        definition = BenchmarkDefinitionEntry.objects.all().first()

        self.assertEqual(1, BenchmarkDefinitionEntry.objects.all().count())
        self.assertEqual(6, BenchmarkExecutionEntry.objects.all().count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(commit=self.commit1, definition=definition, worker=self.worker1).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(commit=self.commit2, definition=definition, worker=self.worker1).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(commit=self.commit3, definition=definition, worker=self.worker1).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(commit=self.commit1, definition=definition, worker=self.worker2).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(commit=self.commit2, definition=definition, worker=self.worker2).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(commit=self.commit3, definition=definition, worker=self.worker2).count())


    def test_save_benchmark_definition(self):
        layout = BluesteelLayoutController.create_new_default_layout()
        definition = BenchmarkDefinitionController.create_default_benchmark_definition()

        self.assertEqual('default-name', definition.name)
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-1').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-2').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-3').count())

        project = BluesteelProjectEntry.objects.filter(layout=layout).first()

        obj = {}
        obj['name'] = 'new-name-1'
        obj['layout_id'] = layout.id
        obj['project_id'] = project.id
        obj['command_list'] = []
        obj['command_list'].append('command-28')
        obj['command_list'].append('command-29')
        obj['command_list'].append('command-30')
        obj['command_list'].append('command-31')

        resp = self.client.post(
            '/main/definition/{0}/save/'.format(definition.id),
            data = json.dumps(obj),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])

        definition = BenchmarkDefinitionEntry.objects.filter(id=definition.id).first()

        self.assertEqual('new-name-1', definition.name)

        self.assertEqual(0, CommandEntry.objects.filter(command_set=definition.command_set, command='command-1').count())
        self.assertEqual(0, CommandEntry.objects.filter(command_set=definition.command_set, command='command-2').count())
        self.assertEqual(0, CommandEntry.objects.filter(command_set=definition.command_set, command='command-3').count())

        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-28').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-29').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-30').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-31').count())


    def test_delete_benchmark_definition_also_deletes_benchmark_executions(self):
        layout = BluesteelLayoutController.create_new_default_layout()
        definition = BenchmarkDefinitionController.create_default_benchmark_definition()

        BenchmarkExecutionController.create_benchmark_execution(definition, self.commit1, self.worker1)
        BenchmarkExecutionController.create_benchmark_execution(definition, self.commit2, self.worker1)
        BenchmarkExecutionController.create_benchmark_execution(definition, self.commit3, self.worker1)
        BenchmarkExecutionController.create_benchmark_execution(definition, self.commit1, self.worker2)
        BenchmarkExecutionController.create_benchmark_execution(definition, self.commit2, self.worker2)
        BenchmarkExecutionController.create_benchmark_execution(definition, self.commit3, self.worker2)

        self.assertEqual(6, BenchmarkExecutionEntry.objects.all().count())

        resp = self.client.post(
            '/main/definition/{0}/delete/'.format(definition.id),
            data = '',
            content_type='application/json')

        self.assertEqual(0, BenchmarkDefinitionEntry.objects.all().count())
        self.assertEqual(0, BenchmarkExecutionEntry.objects.all().count())
