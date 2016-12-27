""" Presenter Views BenchmarkDefinition tests """

from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from django.utils import timezone
from app.logic.benchmark.controllers.BenchmarkDefinitionController import BenchmarkDefinitionController
from app.logic.benchmark.controllers.BenchmarkExecutionController import BenchmarkExecutionController
from app.logic.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.logic.benchmark.models.BenchmarkDefinitionWorkerPassModel import BenchmarkDefinitionWorkerPassEntry
from app.logic.benchmark.models.BenchmarkExecutionModel import BenchmarkExecutionEntry
from app.logic.benchmark.models.BenchmarkFluctuationOverrideModel import BenchmarkFluctuationOverrideEntry
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

        blueProject = BluesteelProjectEntry.objects.all().first().git_project
        commit1 = GitCommitEntry.objects.create(project=blueProject, commit_hash='0000500005000050000500005000050000500005', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())
        commit2 = GitCommitEntry.objects.create(project=blueProject, commit_hash='0000600006000060000600006000060000600006', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())
        commit3 = GitCommitEntry.objects.create(project=blueProject, commit_hash='0000700007000070000700007000070000700007', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())

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
        self.assertEqual(0, BenchmarkExecutionEntry.objects.all().count())
        self.assertEqual(2, BenchmarkDefinitionWorkerPassEntry.objects.all().count())
        self.assertEqual(1, BenchmarkDefinitionWorkerPassEntry.objects.filter(definition=definition, worker=self.worker1).count())
        self.assertEqual(1, BenchmarkDefinitionWorkerPassEntry.objects.filter(definition=definition, worker=self.worker2).count())


    def test_save_benchmark_definition(self):
        layout = BluesteelLayoutController.create_new_default_layout()
        definition = BenchmarkDefinitionController.create_default_benchmark_definition()

        self.assertEqual('default-name', definition.name)
        self.assertEqual(False, definition.active)
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-1').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-2').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-3').count())
        self.assertEqual(0, BenchmarkFluctuationOverrideEntry.objects.all().count())

        project = BluesteelProjectEntry.objects.filter(layout=layout).first()

        obj = {}
        obj['name'] = 'new-name-1'
        obj['layout_id'] = layout.id
        obj['project_id'] = project.id
        obj['active'] = True
        obj['max_fluctuation_percent'] = 28
        obj['max_weeks_old_notify'] = 8
        obj['command_list'] = []
        obj['command_list'].append('command-28')
        obj['command_list'].append('command-29')
        obj['command_list'].append('command-30')
        obj['command_list'].append('command-31')
        obj['overrides'] = []
        obj['overrides'].append({'result_id' : 'id1', 'override_value' : 28})
        obj['overrides'].append({'result_id' : 'id2', 'override_value' : 29})
        obj['work_passes'] = []

        resp = self.client.post(
            '/main/definition/{0}/save/'.format(definition.id),
            data = json.dumps(obj),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])

        definition = BenchmarkDefinitionEntry.objects.filter(id=definition.id).first()

        self.assertEqual('new-name-1', definition.name)
        self.assertEqual(True, definition.active)
        self.assertEqual(28, definition.max_fluctuation_percent)
        self.assertEqual(8, definition.max_weeks_old_notify)

        self.assertEqual(0, CommandEntry.objects.filter(command_set=definition.command_set, command='command-1').count())
        self.assertEqual(0, CommandEntry.objects.filter(command_set=definition.command_set, command='command-2').count())
        self.assertEqual(0, CommandEntry.objects.filter(command_set=definition.command_set, command='command-3').count())

        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-28').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-29').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-30').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-31').count())

        self.assertEqual(2, BenchmarkFluctuationOverrideEntry.objects.all().count())
        self.assertEqual(1, BenchmarkFluctuationOverrideEntry.objects.filter(result_id='id1', override_value=28).count())
        self.assertEqual(1, BenchmarkFluctuationOverrideEntry.objects.filter(result_id='id2', override_value=29).count())


    def test_save_benchmark_definition_with_longest_override_id_possible(self):
        layout = BluesteelLayoutController.create_new_default_layout()
        definition = BenchmarkDefinitionController.create_default_benchmark_definition()

        project = BluesteelProjectEntry.objects.filter(layout=layout).first()

        long_id = 'a' * 255

        obj = {}
        obj['name'] = 'new-name-1'
        obj['layout_id'] = layout.id
        obj['project_id'] = project.id
        obj['active'] = True
        obj['max_fluctuation_percent'] = 28
        obj['max_weeks_old_notify'] = 8
        obj['command_list'] = []
        obj['command_list'].append('command-28')
        obj['overrides'] = []
        obj['overrides'].append({'result_id' : long_id, 'override_value' : 28})
        obj['work_passes'] = []

        resp = self.client.post(
            '/main/definition/{0}/save/'.format(definition.id),
            data = json.dumps(obj),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])

        self.assertEqual(1, BenchmarkFluctuationOverrideEntry.objects.all().count())
        self.assertEqual(1, BenchmarkFluctuationOverrideEntry.objects.filter(result_id=long_id, override_value=28).count())
        self.assertEqual(long_id, BenchmarkFluctuationOverrideEntry.objects.all().first().result_id)

    def test_save_benchmark_definition_with_too_long_override_id(self):
        layout = BluesteelLayoutController.create_new_default_layout()
        definition = BenchmarkDefinitionController.create_default_benchmark_definition()

        project = BluesteelProjectEntry.objects.filter(layout=layout).first()

        long_id = 'a' * 256

        obj = {}
        obj['name'] = 'new-name-1'
        obj['layout_id'] = layout.id
        obj['project_id'] = project.id
        obj['active'] = True
        obj['max_fluctuation_percent'] = 28
        obj['max_weeks_old_notify'] = 8
        obj['command_list'] = []
        obj['command_list'].append('command-28')
        obj['overrides'] = []
        obj['overrides'].append({'result_id' : long_id, 'override_value' : 28})
        obj['work_passes'] = []

        resp = self.client.post(
            '/main/definition/{0}/save/'.format(definition.id),
            data = json.dumps(obj),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(406, resp_obj['status'])


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

    def test_get_workes_only_associated_with_a_benchmark_definition(self):
        layout = BluesteelLayoutController.create_new_default_layout()
        definition = BenchmarkDefinitionController.create_default_benchmark_definition()

        BenchmarkDefinitionWorkerPassEntry.objects.create(definition=definition, worker=self.worker1, allowed=True)
        BenchmarkDefinitionWorkerPassEntry.objects.create(definition=definition, worker=self.worker2, allowed=False)

        resp = self.client.get('/main/definition/{0}/workers/list/'.format(definition.id))

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(1, len(resp_obj['data']['workers']))
        self.assertEqual(self.worker1.id, resp_obj['data']['workers'][0]['id'])
        self.assertEqual('worker-name-1', resp_obj['data']['workers'][0]['name'])
        self.assertEqual('osx', resp_obj['data']['workers'][0]['operative_system'])
