""" Presenter PrepareObjects tests """

from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from django.utils import timezone
from app.logic.benchmark.controllers.BenchmarkDefinitionController import BenchmarkDefinitionController
from app.logic.benchmark.controllers.BenchmarkExecutionController import BenchmarkExecutionController
from app.logic.bluesteel.controllers.BluesteelLayoutController import BluesteelLayoutController
from app.logic.bluesteel.controllers.BluesteelProjectController import BluesteelProjectController
from app.logic.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.logic.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.logic.benchmark.models.BenchmarkExecutionModel import BenchmarkExecutionEntry
from app.logic.gitrepo.models.GitProjectModel import GitProjectEntry
from app.logic.gitrepo.models.GitUserModel import GitUserEntry
from app.logic.gitrepo.models.GitCommitModel import GitCommitEntry
from app.logic.commandrepo.models.CommandModel import CommandEntry
from app.logic.commandrepo.models.CommandResultModel import CommandResultEntry
from app.logic.commandrepo.models.CommandSetModel import CommandSetEntry
from app.logic.commandrepo.models.CommandGroupModel import CommandGroupEntry
from app.logic.bluesteelworker.models.WorkerModel import WorkerEntry
from app.logic.httpcommon import res
from app.presenter.views.helpers import ViewPrepareObjects
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

        self.worker1 = WorkerEntry.objects.create(
            name='worker-name-1',
            uuid='uuid-worker-1',
            operative_system='osx',
            description='long-description-1',
            user=self.user1,
            git_feeder=False
        )

        self.bluesteel_layout1 = BluesteelLayoutController.create_new_default_layout()
        self.benchmark_definition1 = BenchmarkDefinitionController.create_default_benchmark_definition()

    def tearDown(self):
        pass

    def create_command_result(self, command, status, out, error):
        command_group = CommandGroupEntry.objects.create()
        command_set = CommandSetEntry.objects.create(group=command_group)

        command1 = CommandEntry.objects.create(
            command_set=command_set,
            command=command,
            order=0)

        command_result = CommandResultEntry.objects.create(
            command=command1,
            out=json.dumps(out),
            error=error,
            status=status,
            start_time=timezone.now(),
            finish_time=timezone.now())

        return command_set


    def test_prepare_objects_from_benchmark_execution_vertical_bars(self):
        obj = [{'vertical_bars' : {'data' : [1, 2, 3, 4, 5]}}]

        command_set = self.create_command_result('command-1', 0, obj, 'no error')

        exec_entry = BenchmarkExecutionEntry.objects.create(
            definition=self.benchmark_definition1,
            commit=self.commit1,
            worker=self.worker1,
            report=command_set)

        exec_obj = exec_entry.as_object()
        results = ViewPrepareObjects.prepare_results_from_bench_exec_to_html(exec_obj)

        self.assertEqual('command-1', results[0]['command'])
        self.assertEqual(0, results[0]['status'])
        self.assertEqual('no error', results[0]['error'])
        self.assertEqual([1, 2, 3, 4, 5], results[0]['out'][0]['obj']['vertical_bars']['data'])
        self.assertEqual('{"vertical_bars": {"data": [1, 2, 3, 4, 5]}}', results[0]['out'][0]['json'])

    def test_prepare_objects_from_benchmark_execution_text(self):
        obj = [{'text' : {'data' : 'this is a text!!'}}]

        command_set = self.create_command_result('command-2', 0, obj, 'no no error')

        exec_entry = BenchmarkExecutionEntry.objects.create(
            definition=self.benchmark_definition1,
            commit=self.commit1,
            worker=self.worker1,
            report=command_set)

        exec_obj = exec_entry.as_object()
        results = ViewPrepareObjects.prepare_results_from_bench_exec_to_html(exec_obj)

        self.assertEqual('command-2', results[0]['command'])
        self.assertEqual(0, results[0]['status'])
        self.assertEqual('no no error', results[0]['error'])
        self.assertEqual('this is a text!!', results[0]['out'][0]['obj']['text']['data'])
        self.assertEqual('{"text": {"data": "this is a text!!"}}', results[0]['out'][0]['json'])

    def test_prepare_objects_from_benchmark_execution_from_plain_text(self):
        command_group = CommandGroupEntry.objects.create()
        command_set = CommandSetEntry.objects.create(group=command_group)

        command1 = CommandEntry.objects.create(
            command_set=command_set,
            command='command-1',
            order=0)

        command_result = CommandResultEntry.objects.create(
            command=command1,
            out='this is a plain text and it is not json!',
            error='nop, no error',
            status=0,
            start_time=timezone.now(),
            finish_time=timezone.now())

        exec_entry = BenchmarkExecutionEntry.objects.create(
            definition=self.benchmark_definition1,
            commit=self.commit1,
            worker=self.worker1,
            report=command_set)

        exec_obj = exec_entry.as_object()
        results = ViewPrepareObjects.prepare_results_from_bench_exec_to_html(exec_obj)

        self.assertEqual('command-1', results[0]['command'])
        self.assertEqual(0, results[0]['status'])
        self.assertEqual('nop, no error', results[0]['error'])
        self.assertEqual('No JSON object could be decoded\nthis is a plain text and it is not json!', results[0]['out'][0]['obj']['text']['data'])
        self.assertEqual('{"text": {"data": "No JSON object could be decoded\\nthis is a plain text and it is not json!"}}', results[0]['out'][0]['json'])

    def test_prepare_objects_from_benchmark_execution_with_command_substitution(self):
        obj = [{'vertical_bars' : {'data' : [1, 2, 3, 4, 5]}}]

        command_set = self.create_command_result('command-1 {commit}', 0, obj, 'no error')

        exec_entry = BenchmarkExecutionEntry.objects.create(
            definition=self.benchmark_definition1,
            commit=self.commit1,
            worker=self.worker1,
            report=command_set)

        exec_obj = exec_entry.as_object()
        results = ViewPrepareObjects.prepare_results_from_bench_exec_to_html(exec_obj)

        self.assertEqual('command-1 0000100001000010000100001000010000100001', results[0]['command'])
        self.assertEqual(0, results[0]['status'])
        self.assertEqual('no error', results[0]['error'])
        self.assertEqual([1, 2, 3, 4, 5], results[0]['out'][0]['obj']['vertical_bars']['data'])
        self.assertEqual('{"vertical_bars": {"data": [1, 2, 3, 4, 5]}}', results[0]['out'][0]['json'])
