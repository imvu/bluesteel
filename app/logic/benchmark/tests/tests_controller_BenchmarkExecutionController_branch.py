""" BenchmarkExecution Branch Controller tests """

from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth.models import AnonymousUser
from app.logic.benchmark.controllers.BenchmarkExecutionController import BenchmarkExecutionController
from app.logic.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.logic.benchmark.models.BenchmarkExecutionModel import BenchmarkExecutionEntry
from app.logic.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.logic.bluesteel.controllers.BluesteelProjectController import BluesteelProjectController
from app.logic.gitrepo.models.GitProjectModel import GitProjectEntry
from app.logic.gitrepo.models.GitUserModel import GitUserEntry
from app.logic.gitrepo.models.GitCommitModel import GitCommitEntry
from app.logic.gitrepo.models.GitBranchModel import GitBranchEntry
from app.logic.gitrepo.models.GitBranchTrailModel import GitBranchTrailEntry
from app.logic.commandrepo.models.CommandModel import CommandEntry
from app.logic.commandrepo.models.CommandResultModel import CommandResultEntry
from app.logic.commandrepo.models.CommandSetModel import CommandSetEntry
from app.logic.commandrepo.models.CommandGroupModel import CommandGroupEntry
from app.logic.commandrepo.helper import TestCommandHelper
from app.logic.bluesteelworker.models.WorkerModel import WorkerEntry
from django.utils import timezone
import json

class BenchmarkExecutionControllerBranchTestCase(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user('user1@test.com', 'user1@test.com', 'pass')
        self.user1.save()

        self.user2 = User.objects.create_user('user2@test.com', 'user2@test.com', 'pass')
        self.user2.save()

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

        self.branch1 = GitBranchEntry.objects.create(
            project=self.git_project1,
            name='branch1',
            commit=self.commit3
        )

        self.trail1 = GitBranchTrailEntry.objects.create(
            project=self.git_project1,
            branch=self.branch1,
            commit=self.commit1,
            order=0
        )

        self.trail2 = GitBranchTrailEntry.objects.create(
            project=self.git_project1,
            branch=self.branch1,
            commit=self.commit2,
            order=1
        )

        self.trail3 = GitBranchTrailEntry.objects.create(
            project=self.git_project1,
            branch=self.branch1,
            commit=self.commit3,
            order=2
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

        self.benchmark_definition1 = BenchmarkDefinitionEntry.objects.create(
            name='BenchmarkDefinition1',
            layout=self.bluesteel_layout,
            project=self.bluesteel_project,
            command_set=self.command_set,
            revision=28,
        )

        self.benchmark_definition2 = BenchmarkDefinitionEntry.objects.create(
            name='BenchmarkDefinition2',
            layout=self.bluesteel_layout,
            project=self.bluesteel_project,
            command_set=self.command_set,
            revision=3,
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
            user=self.user2,
            git_feeder=False
        )

        self.report_1 = CommandSetEntry.objects.create(group=None)
        self.report_2 = CommandSetEntry.objects.create(group=None)
        self.report_3 = CommandSetEntry.objects.create(group=None)

        self.com1 = CommandEntry.objects.create(
            command_set=self.report_1,
            command='command1',
            order=0
        )

        self.com2 = CommandEntry.objects.create(
            command_set=self.report_2,
            command='command2',
            order=1
        )

        self.com3 = CommandEntry.objects.create(
            command_set=self.report_3,
            command='command3',
            order=2
        )

        self.benchmark_execution1 = BenchmarkExecutionEntry.objects.create(
            definition=self.benchmark_definition1,
            commit=self.commit1,
            worker=self.worker1,
            report=self.report_1,
            invalidated=False,
            revision_target=28,
            status=BenchmarkExecutionEntry.READY,
        )

        self.benchmark_execution2 = BenchmarkExecutionEntry.objects.create(
            definition=self.benchmark_definition1,
            commit=self.commit2,
            worker=self.worker1,
            report=self.report_2,
            invalidated=False,
            revision_target=28,
            status=BenchmarkExecutionEntry.READY,
        )

        self.benchmark_execution3 = BenchmarkExecutionEntry.objects.create(
            definition=self.benchmark_definition1,
            commit=self.commit3,
            worker=self.worker1,
            report=self.report_3,
            invalidated=False,
            revision_target=2,
            status=BenchmarkExecutionEntry.READY,
        )

    def tearDown(self):
        pass

    def test_get_benchmark_execution_from_branch_same_id(self):
        out_1 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1,2,3,4,5]}])
        out_2 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [6,7,8,9,10]}])
        out_3 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [11,12,13,14,15]}])

        res1 = CommandResultEntry.objects.create(
            command=self.com1,
            out=out_1,
            error='no error',
            status=0,
            start_time=timezone.now(),
            finish_time=timezone.now()
        )

        res2 = CommandResultEntry.objects.create(
            command=self.com2,
            out=out_2,
            error='no error',
            status=0,
            start_time=timezone.now(),
            finish_time=timezone.now()
        )

        res3 = CommandResultEntry.objects.create(
            command=self.com3,
            out=out_3,
            error='no error',
            status=0,
            start_time=timezone.now(),
            finish_time=timezone.now()
        )

        self.benchmark_execution1.report = self.report_1
        self.benchmark_execution1.save()

        self.benchmark_execution2.report = self.report_2
        self.benchmark_execution2.save()

        self.benchmark_execution3.report = self.report_3
        self.benchmark_execution3.save()

        bench_data = BenchmarkExecutionController.get_benchmark_execution_from_branch(
            self.git_project1,
            self.branch1,
            self.benchmark_definition1,
            self.worker1
        )

        self.assertEqual(3, len(bench_data['id1']))
        self.assertEqual(3.0, bench_data['id1'][0]['average'])
        self.assertEqual(8.0, bench_data['id1'][1]['average'])
        self.assertEqual(13.0, bench_data['id1'][2]['average'])
        self.assertEqual(self.benchmark_execution1.id, bench_data['id1'][0]['benchmark_execution_id'])
        self.assertEqual(self.benchmark_execution2.id, bench_data['id1'][1]['benchmark_execution_id'])
        self.assertEqual(self.benchmark_execution3.id, bench_data['id1'][2]['benchmark_execution_id'])


    def test_get_benchmark_execution_from_branch_different_id(self):
        out_1 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1,2,3,4,5]}])
        out_2 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id2', 'data' : [6,7,8,9,10]}])
        out_3 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id3', 'data' : [11,12,13,14,15]}])

        res1 = CommandResultEntry.objects.create(
            command=self.com1,
            out=out_1,
            error='no error',
            status=0,
            start_time=timezone.now(),
            finish_time=timezone.now()
        )

        res2 = CommandResultEntry.objects.create(
            command=self.com2,
            out=out_2,
            error='no error',
            status=0,
            start_time=timezone.now(),
            finish_time=timezone.now()
        )

        res3 = CommandResultEntry.objects.create(
            command=self.com3,
            out=out_3,
            error='no error',
            status=0,
            start_time=timezone.now(),
            finish_time=timezone.now()
        )

        self.benchmark_execution1.report = self.report_1
        self.benchmark_execution1.save()

        self.benchmark_execution2.report = self.report_2
        self.benchmark_execution2.save()

        self.benchmark_execution3.report = self.report_3
        self.benchmark_execution3.save()

        bench_data = BenchmarkExecutionController.get_benchmark_execution_from_branch(
            self.git_project1,
            self.branch1,
            self.benchmark_definition1,
            self.worker1
        )

        self.assertEqual(3, len(bench_data['id1']))
        self.assertEqual(3.0, bench_data['id1'][0]['average'])
        self.assertEqual(0.0, bench_data['id1'][1]['average'])
        self.assertEqual(0.0, bench_data['id1'][2]['average'])
        self.assertEqual(self.benchmark_execution1.id, bench_data['id1'][0]['benchmark_execution_id'])
        self.assertEqual(0, bench_data['id1'][1]['benchmark_execution_id'])
        self.assertEqual(0, bench_data['id1'][2]['benchmark_execution_id'])

        self.assertEqual(3, len(bench_data['id2']))
        self.assertEqual(0.0, bench_data['id2'][0]['average'])
        self.assertEqual(8.0, bench_data['id2'][1]['average'])
        self.assertEqual(0.0, bench_data['id2'][2]['average'])
        self.assertEqual(0, bench_data['id2'][0]['benchmark_execution_id'])
        self.assertEqual(self.benchmark_execution2.id, bench_data['id2'][1]['benchmark_execution_id'])
        self.assertEqual(0, bench_data['id2'][2]['benchmark_execution_id'])

        self.assertEqual(3, len(bench_data['id3']))
        self.assertEqual(0.0, bench_data['id3'][0]['average'])
        self.assertEqual(0.0, bench_data['id3'][1]['average'])
        self.assertEqual(13.0, bench_data['id3'][2]['average'])
        self.assertEqual(0, bench_data['id3'][0]['benchmark_execution_id'])
        self.assertEqual(0, bench_data['id3'][1]['benchmark_execution_id'])
        self.assertEqual(self.benchmark_execution3.id, bench_data['id3'][2]['benchmark_execution_id'])
