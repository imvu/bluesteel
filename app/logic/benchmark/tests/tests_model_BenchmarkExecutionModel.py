""" BenchmarkExecution Model tests """

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from app.logic.benchmark.models.BenchmarkExecutionModel import BenchmarkExecutionEntry
from app.logic.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.logic.gitrepo.models.GitProjectModel import GitProjectEntry
from app.logic.gitrepo.models.GitUserModel import GitUserEntry
from app.logic.gitrepo.models.GitCommitModel import GitCommitEntry
from app.logic.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.logic.bluesteelworker.models.WorkerModel import WorkerEntry
from app.logic.commandrepo.models.CommandGroupModel import CommandGroupEntry
from app.logic.commandrepo.models.CommandSetModel import CommandSetEntry
from app.logic.commandrepo.models.CommandModel import CommandEntry
from app.logic.commandrepo.models.CommandResultModel import CommandResultEntry
from datetime import timedelta
import json

class BenchmarkExecutionEntryTestCase(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user('user1@test.com', 'user1@test.com', 'pass')
        self.user1.save()

        self.git_project = GitProjectEntry.objects.create(url='http://test/')
        self.git_user = GitUserEntry.objects.create(
            project=self.git_project,
            name='user1',
            email='user1@test.com'
        )

        self.git_commit = GitCommitEntry.objects.create(
            project=self.git_project,
            commit_hash='0000100001000010000100001000010000100001',
            author=self.git_user,
            author_date=timezone.now(),
            committer=self.git_user,
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
            git_project=self.git_project,
        )

        self.benchmark_definition = BenchmarkDefinitionEntry.objects.create(
            name='BenchmarkDefinition',
            layout=self.bluesteel_layout,
            project=self.bluesteel_project,
            command_set=self.command_set,
        )

        self.worker = WorkerEntry.objects.create(
            name='worker-name',
            uuid='uuid-worker',
            operative_system='unix',
            description='long description',
            user=self.user1,
            git_feeder=False
        )


    def tearDown(self):
        pass

    def test_benchmark_execution_as_object(self):
        entry = BenchmarkExecutionEntry.objects.create(
            definition=self.benchmark_definition,
            commit=self.git_commit,
            worker=self.worker,
            report=self.command_set,
            invalidated=False,
            status=BenchmarkExecutionEntry.STATUS_TYPE[1][0]
        )

        obj = entry.as_object()

        self.assertEqual('0000100001000010000100001000010000100001', obj['commit'])
        self.assertEqual('project-1', obj['definition']['project']['uuid'])
        self.assertEqual(1, obj['definition']['project']['id'])
        self.assertEqual('http://test/', obj['definition']['project']['git_project']['url'])
        self.assertEqual(0, len(obj['definition']['project']['git_project']['branches']) )
        self.assertEqual('default-name', obj['definition']['project']['git_project']['name'])
        self.assertEqual(0, len(obj['report']['commands']))
        self.assertEqual(True, obj['invalidated'])
        self.assertEqual(1, obj['status']['index'])
        self.assertEqual('In_Progress', obj['status']['name'])
        self.assertEqual(1, obj['worker']['id'])
        self.assertEqual('worker-name', obj['worker']['name'])
        self.assertEqual('uuid-worker', obj['worker']['uuid'])
        self.assertEqual('unix', obj['worker']['operative_system'])
        self.assertEqual('long description', obj['worker']['description'])
        self.assertEqual(False, obj['worker']['git_feeder'])


    def test_benchmark_execution_invalidated_by_bool_property(self):
        self.benchmark_definition.revision = 28
        self.benchmark_definition.save()

        entry = BenchmarkExecutionEntry.objects.create(
            definition=self.benchmark_definition,
            commit=self.git_commit,
            worker=self.worker,
            report=self.command_set,
            invalidated=True,
            status=BenchmarkExecutionEntry.STATUS_TYPE[1][0],
            revision_target=28
        )

        self.assertEqual(True, entry.is_invalidated())

    def test_benchmark_execution_invalidated_by_revision(self):
        self.benchmark_definition.revision = 29
        self.benchmark_definition.save()

        entry = BenchmarkExecutionEntry.objects.create(
            definition=self.benchmark_definition,
            commit=self.git_commit,
            worker=self.worker,
            report=self.command_set,
            invalidated=False,
            status=BenchmarkExecutionEntry.STATUS_TYPE[1][0],
            revision_target=28
        )

        self.assertEqual(True, entry.is_invalidated())

    def test_get_benchmark_results_comput_vertical_bars_average(self):
        out1 = {}
        out1['id'] = 'benchmark-res-id-1'
        out1['visual_type'] = 'vertical_bars'
        out1['data'] = [1, 2, 3, 4, 5.5]

        out2 = {}
        out2['id'] = 'benchmark-res-id-2'
        out2['visual_type'] = 'text'
        out2['data'] = 'this is a text'

        out1str = json.dumps([out1])
        out2str = json.dumps([out2])

        command_group1 = CommandGroupEntry.objects.create()
        command_set1 = CommandSetEntry.objects.create(group=command_group1)

        command1 = CommandEntry.objects.create(command_set=command_set1, command='command 1', order=0)
        command2 = CommandEntry.objects.create(command_set=command_set1, command='command 2', order=1)

        command_res1 = CommandResultEntry.objects.create(command=command1, out=out1str, error='', status=0)
        command_res2 = CommandResultEntry.objects.create(command=command2, out=out2str, error='', status=0)


        bench_entry = BenchmarkExecutionEntry.objects.create(
            definition=self.benchmark_definition,
            commit=self.git_commit,
            worker=self.worker,
            report=command_set1,
            invalidated=False,
            status=BenchmarkExecutionEntry.STATUS_TYPE[1][0],
            revision_target=28
        )

        results = bench_entry.get_benchmark_results()

        self.assertEqual(2, len(results))
        self.assertEqual('benchmark-res-id-1', results[0]['id'])
        self.assertEqual('vertical_bars', results[0]['visual_type'])
        self.assertEqual([1, 2, 3, 4, 5.5], results[0]['data'])
        self.assertEqual(3.1, results[0]['average'])

        self.assertEqual('benchmark-res-id-2', results[1]['id'])
        self.assertEqual('text', results[1]['visual_type'])
        self.assertEqual('this is a text', results[1]['data'])


    def test_benchmark_execution_deletion_also_delete_the_report(self):
        report = CommandSetEntry.objects.create()

        entry = BenchmarkExecutionEntry.objects.create(
            definition=self.benchmark_definition,
            commit=self.git_commit,
            worker=self.worker,
            report=report,
            invalidated=False,
            status=BenchmarkExecutionEntry.STATUS_TYPE[1][0]
        )

        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(id=entry.id).count())
        self.assertEqual(1, CommandSetEntry.objects.filter(id=report.id).count())
        entry.delete()
        self.assertEqual(0, BenchmarkExecutionEntry.objects.filter(id=entry.id).count())
        self.assertEqual(0, CommandSetEntry.objects.filter(id=report.id).count())
