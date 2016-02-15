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
from app.logic.gitrepo.models.GitBranchMergeTargetModel import GitBranchMergeTargetEntry
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

    def test_get_stacked_benchmark_execution_from_branch(self):
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

        bench_data = BenchmarkExecutionController.get_stacked_executions_from_branch(
            self.git_project1,
            self.branch1,
            self.benchmark_definition1,
            self.worker1
        )

        self.assertEqual(3, len(bench_data))
        self.assertEqual(True, bench_data[0]['current_branch'])
        self.assertEqual(True, bench_data[0]['exists'])
        self.assertEqual('0000100001000010000100001000010000100001', bench_data[0]['commit'])
        self.assertEqual(self.benchmark_execution1.id, bench_data[0]['benchmark_execution_id'])
        self.assertEqual([1,2,3,4,5], json.loads(bench_data[0]['report']['commands'][0]['result']['out'])[0]['data'])

        self.assertEqual(True, bench_data[1]['current_branch'])
        self.assertEqual(True, bench_data[1]['exists'])
        self.assertEqual('0000200002000020000200002000020000200002', bench_data[1]['commit'])
        self.assertEqual(self.benchmark_execution2.id, bench_data[1]['benchmark_execution_id'])
        self.assertEqual([6,7,8,9,10], json.loads(bench_data[1]['report']['commands'][0]['result']['out'])[0]['data'])

        self.assertEqual(True, bench_data[2]['current_branch'])
        self.assertEqual(True, bench_data[2]['exists'])
        self.assertEqual('0000300003000030000300003000030000300003', bench_data[2]['commit'])
        self.assertEqual(self.benchmark_execution3.id, bench_data[2]['benchmark_execution_id'])
        self.assertEqual([11,12,13,14,15], json.loads(bench_data[2]['report']['commands'][0]['result']['out'])[0]['data'])


    def test_get_stacked_benchmark_execution_from_branch_with_deleted_benchmarks(self):
        out_1 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1,2,3,4,5]}])
        out_3 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [11,12,13,14,15]}])

        res1 = CommandResultEntry.objects.create(command=self.com1, out=out_1, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        res3 = CommandResultEntry.objects.create(command=self.com3, out=out_3, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())

        self.benchmark_execution1.report = self.report_1
        self.benchmark_execution1.save()

        self.benchmark_execution2.delete()

        self.benchmark_execution3.report = self.report_3
        self.benchmark_execution3.save()

        bench_data = BenchmarkExecutionController.get_stacked_executions_from_branch(
            self.git_project1,
            self.branch1,
            self.benchmark_definition1,
            self.worker1
        )

        self.assertEqual(3, len(bench_data))
        self.assertEqual(True, bench_data[0]['current_branch'])
        self.assertEqual(True, bench_data[0]['exists'])
        self.assertEqual('0000100001000010000100001000010000100001', bench_data[0]['commit'])
        self.assertEqual(self.benchmark_execution1.id, bench_data[0]['benchmark_execution_id'])
        self.assertEqual([1,2,3,4,5], json.loads(bench_data[0]['report']['commands'][0]['result']['out'])[0]['data'])

        self.assertEqual(False, bench_data[1]['current_branch'])
        self.assertEqual(False, bench_data[1]['exists'])

        self.assertEqual(True, bench_data[2]['current_branch'])
        self.assertEqual(True, bench_data[2]['exists'])
        self.assertEqual('0000300003000030000300003000030000300003', bench_data[2]['commit'])
        self.assertEqual(self.benchmark_execution3.id, bench_data[2]['benchmark_execution_id'])
        self.assertEqual([11,12,13,14,15], json.loads(bench_data[2]['report']['commands'][0]['result']['out'])[0]['data'])


    def test_get_stacked_data_different_id(self):
        out_1 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1,2,3,4,5]}])
        out_2 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id2', 'data' : [6,7,8,9,10]}])
        out_3 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id3', 'data' : [11,12,13,14,15]}])

        res1 = CommandResultEntry.objects.create(command=self.com1, out=out_1, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        res2 = CommandResultEntry.objects.create(command=self.com2, out=out_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        res3 = CommandResultEntry.objects.create(command=self.com3, out=out_3, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())

        self.benchmark_execution1.report = self.report_1
        self.benchmark_execution1.save()

        self.benchmark_execution2.report = self.report_2
        self.benchmark_execution2.save()

        self.benchmark_execution3.report = self.report_3
        self.benchmark_execution3.save()

        data = BenchmarkExecutionController.get_stacked_executions_from_branch(
            self.git_project1,
            self.branch1,
            self.benchmark_definition1,
            self.worker1
        )

        bench_data = BenchmarkExecutionController.get_stacked_data_separated_by_id(data)

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

    def test_get_stacked_data_same_id(self):
        out_1 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1,2,3,4,5]}])
        out_2 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [6,7,8,9,10]}])
        out_3 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [11,12,13,14,15]}])

        res1 = CommandResultEntry.objects.create(command=self.com1, out=out_1, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        res2 = CommandResultEntry.objects.create(command=self.com2, out=out_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        res3 = CommandResultEntry.objects.create(command=self.com3, out=out_3, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())

        self.benchmark_execution1.report = self.report_1
        self.benchmark_execution1.save()

        self.benchmark_execution2.report = self.report_2
        self.benchmark_execution2.save()

        self.benchmark_execution3.report = self.report_3
        self.benchmark_execution3.save()

        data = BenchmarkExecutionController.get_stacked_executions_from_branch(
            self.git_project1,
            self.branch1,
            self.benchmark_definition1,
            self.worker1
        )

        bench_data = BenchmarkExecutionController.get_stacked_data_separated_by_id(data)

        self.assertEqual(3, len(bench_data['id1']))
        self.assertEqual(3.0, bench_data['id1'][0]['average'])
        self.assertEqual(8.0, bench_data['id1'][1]['average'])
        self.assertEqual(13.0, bench_data['id1'][2]['average'])
        self.assertEqual(self.benchmark_execution1.id, bench_data['id1'][0]['benchmark_execution_id'])
        self.assertEqual(self.benchmark_execution2.id, bench_data['id1'][1]['benchmark_execution_id'])
        self.assertEqual(self.benchmark_execution3.id, bench_data['id1'][2]['benchmark_execution_id'])

    def test_get_stacked_data_multiple_id_per_execution(self):
        out_1 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1,2,3,4,5]},     {'visual_type' : 'vertical_bars', 'id' : 'id4', 'data' : [21,22,23,24,25]}])
        out_2 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [6,7,8,9,10]},    {'visual_type' : 'vertical_bars', 'id' : 'id6', 'data' : [31,32,33,34,35]}])
        out_3 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [11,12,13,14,15]},{'visual_type' : 'vertical_bars', 'id' : 'id8', 'data' : [51,52,53,54,55]}])

        res1 = CommandResultEntry.objects.create(command=self.com1, out=out_1, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        res2 = CommandResultEntry.objects.create(command=self.com2, out=out_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        res3 = CommandResultEntry.objects.create(command=self.com3, out=out_3, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())

        self.benchmark_execution1.report = self.report_1
        self.benchmark_execution1.save()

        self.benchmark_execution2.report = self.report_2
        self.benchmark_execution2.save()

        self.benchmark_execution3.report = self.report_3
        self.benchmark_execution3.save()

        data = BenchmarkExecutionController.get_stacked_executions_from_branch(
            self.git_project1,
            self.branch1,
            self.benchmark_definition1,
            self.worker1
        )

        bench_data = BenchmarkExecutionController.get_stacked_data_separated_by_id(data)

        self.assertEqual(3, len(bench_data['id1']))
        self.assertEqual(3.0, bench_data['id1'][0]['average'])
        self.assertEqual(8.0, bench_data['id1'][1]['average'])
        self.assertEqual(13.0, bench_data['id1'][2]['average'])
        self.assertEqual(self.benchmark_execution1.id, bench_data['id1'][0]['benchmark_execution_id'])
        self.assertEqual(self.benchmark_execution2.id, bench_data['id1'][1]['benchmark_execution_id'])
        self.assertEqual(self.benchmark_execution3.id, bench_data['id1'][2]['benchmark_execution_id'])

        self.assertEqual(3, len(bench_data['id4']))
        self.assertEqual(23.0, bench_data['id4'][0]['average'])
        self.assertEqual(0.0, bench_data['id4'][1]['average'])
        self.assertEqual(0.0, bench_data['id4'][2]['average'])
        self.assertEqual(self.benchmark_execution1.id, bench_data['id4'][0]['benchmark_execution_id'])
        self.assertEqual(0, bench_data['id4'][1]['benchmark_execution_id'])
        self.assertEqual(0, bench_data['id4'][2]['benchmark_execution_id'])

        self.assertEqual(3, len(bench_data['id6']))
        self.assertEqual(0.0, bench_data['id6'][0]['average'])
        self.assertEqual(33.0, bench_data['id6'][1]['average'])
        self.assertEqual(0.0, bench_data['id6'][2]['average'])
        self.assertEqual(0, bench_data['id6'][0]['benchmark_execution_id'])
        self.assertEqual(self.benchmark_execution2.id, bench_data['id6'][1]['benchmark_execution_id'])
        self.assertEqual(0, bench_data['id6'][2]['benchmark_execution_id'])

        self.assertEqual(3, len(bench_data['id8']))
        self.assertEqual(0.0, bench_data['id8'][0]['average'])
        self.assertEqual(0.0, bench_data['id8'][1]['average'])
        self.assertEqual(53.0, bench_data['id8'][2]['average'])
        self.assertEqual(0, bench_data['id8'][0]['benchmark_execution_id'])
        self.assertEqual(0, bench_data['id8'][1]['benchmark_execution_id'])
        self.assertEqual(self.benchmark_execution3.id, bench_data['id8'][2]['benchmark_execution_id'])


    def test_get_stacked_data_text_is_not_stacked(self):
        out_1 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1,2,3,4,5]},     {'visual_type' : 'text', 'id' : 'id1', 'data' : 'my text'}])
        out_2 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [6,7,8,9,10]},    {'visual_type' : 'vertical_bars', 'id' : 'id6', 'data' : [31,32,33,34,35]}])
        out_3 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [11,12,13,14,15]},{'visual_type' : 'vertical_bars', 'id' : 'id8', 'data' : [51,52,53,54,55]}])

        res1 = CommandResultEntry.objects.create(command=self.com1, out=out_1, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        res2 = CommandResultEntry.objects.create(command=self.com2, out=out_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        res3 = CommandResultEntry.objects.create(command=self.com3, out=out_3, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())

        self.benchmark_execution1.report = self.report_1
        self.benchmark_execution1.save()

        self.benchmark_execution2.report = self.report_2
        self.benchmark_execution2.save()

        self.benchmark_execution3.report = self.report_3
        self.benchmark_execution3.save()

        data = BenchmarkExecutionController.get_stacked_executions_from_branch(
            self.git_project1,
            self.branch1,
            self.benchmark_definition1,
            self.worker1
        )

        bench_data = BenchmarkExecutionController.get_stacked_data_separated_by_id(data)

        self.assertEqual(3, len(bench_data['id1']))
        self.assertEqual(3.0, bench_data['id1'][0]['average'])
        self.assertEqual(8.0, bench_data['id1'][1]['average'])
        self.assertEqual(13.0, bench_data['id1'][2]['average'])
        self.assertEqual(self.benchmark_execution1.id, bench_data['id1'][0]['benchmark_execution_id'])
        self.assertEqual(self.benchmark_execution2.id, bench_data['id1'][1]['benchmark_execution_id'])
        self.assertEqual(self.benchmark_execution3.id, bench_data['id1'][2]['benchmark_execution_id'])

        self.assertEqual(False, 'id4' in bench_data)

        self.assertEqual(3, len(bench_data['id6']))
        self.assertEqual(0.0, bench_data['id6'][0]['average'])
        self.assertEqual(33.0, bench_data['id6'][1]['average'])
        self.assertEqual(0.0, bench_data['id6'][2]['average'])
        self.assertEqual(0, bench_data['id6'][0]['benchmark_execution_id'])
        self.assertEqual(self.benchmark_execution2.id, bench_data['id6'][1]['benchmark_execution_id'])
        self.assertEqual(0, bench_data['id6'][2]['benchmark_execution_id'])

        self.assertEqual(3, len(bench_data['id8']))
        self.assertEqual(0.0, bench_data['id8'][0]['average'])
        self.assertEqual(0.0, bench_data['id8'][1]['average'])
        self.assertEqual(53.0, bench_data['id8'][2]['average'])
        self.assertEqual(0, bench_data['id8'][0]['benchmark_execution_id'])
        self.assertEqual(0, bench_data['id8'][1]['benchmark_execution_id'])
        self.assertEqual(self.benchmark_execution3.id, bench_data['id8'][2]['benchmark_execution_id'])

    def test_bar_color_depending_on_branch(self):
        commit4 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000400004000040000400004000040000400004', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())
        commit5 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000500005000050000500005000050000500005', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())
        commit6 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000600006000060000600006000060000600006', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())

        branch2 = GitBranchEntry.objects.create(project=self.git_project1, name='branch2', commit=commit6)
        GitBranchMergeTargetEntry.objects.create(project=self.git_project1, current_branch=branch2, target_branch=self.branch1, fork_point=self.commit3)

        self.trail1_2 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch2, commit=self.commit1, order=5)
        self.trail2_2 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch2, commit=self.commit2, order=4)
        self.trail3_2 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch2, commit=self.commit3, order=3)
        self.trail4_2 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch2, commit=commit4, order=2)
        self.trail5_2 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch2, commit=commit5, order=1)
        self.trail6_2 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch2, commit=commit6, order=0)

        report_1 = CommandSetEntry.objects.create(group=None)
        report_2 = CommandSetEntry.objects.create(group=None)
        report_3 = CommandSetEntry.objects.create(group=None)
        report_4 = CommandSetEntry.objects.create(group=None)
        report_5 = CommandSetEntry.objects.create(group=None)
        report_6 = CommandSetEntry.objects.create(group=None)

        com1 = CommandEntry.objects.create(command_set=report_1, command='command1', order=0)
        com2 = CommandEntry.objects.create(command_set=report_2, command='command2', order=1)
        com3 = CommandEntry.objects.create(command_set=report_3, command='command3', order=2)
        com4 = CommandEntry.objects.create(command_set=report_4, command='command4', order=3)
        com5 = CommandEntry.objects.create(command_set=report_5, command='command5', order=4)
        com6 = CommandEntry.objects.create(command_set=report_6, command='command6', order=5)

        out_1_2 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1,1,1,1,1]}])
        out_2_2 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [2,2,2,2,2]}])
        out_3_2 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [3,3,3,3,3]}])
        out_4_2 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [4,4,4,4,4]}])
        out_5_2 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [5,5,5,5,5]}])
        out_6_2 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [6,6,6,6,6]}])

        CommandResultEntry.objects.create(command=com1, out=out_1_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com2, out=out_2_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com3, out=out_3_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com4, out=out_4_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com5, out=out_5_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com6, out=out_6_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())

        self.benchmark_execution1.report = report_1
        self.benchmark_execution2.report = report_2
        self.benchmark_execution3.report = report_3

        self.benchmark_execution1.save()
        self.benchmark_execution2.save()
        self.benchmark_execution3.save()

        benchmark_execution4 = BenchmarkExecutionEntry.objects.create(
            definition=self.benchmark_definition1,
            commit=commit4,
            worker=self.worker1,
            report=report_4,
            invalidated=False,
            revision_target=28,
            status=BenchmarkExecutionEntry.READY,
        )

        benchmark_execution5 = BenchmarkExecutionEntry.objects.create(
            definition=self.benchmark_definition1,
            commit=commit5,
            worker=self.worker1,
            report=report_5,
            invalidated=False,
            revision_target=28,
            status=BenchmarkExecutionEntry.READY,
        )

        benchmark_execution6 = BenchmarkExecutionEntry.objects.create(
            definition=self.benchmark_definition1,
            commit=commit6,
            worker=self.worker1,
            report=report_6,
            invalidated=False,
            revision_target=2,
            status=BenchmarkExecutionEntry.READY,
        )

        data = BenchmarkExecutionController.get_stacked_executions_from_branch(
            self.git_project1,
            branch2,
            self.benchmark_definition1,
            self.worker1
        )

        bench_data = BenchmarkExecutionController.get_stacked_data_separated_by_id(data)

        self.assertEqual(6.0, bench_data['id1'][0]['average'])
        self.assertEqual(5.0, bench_data['id1'][1]['average'])
        self.assertEqual(4.0, bench_data['id1'][2]['average'])
        self.assertEqual(3.0, bench_data['id1'][3]['average'])
        self.assertEqual(2.0, bench_data['id1'][4]['average'])
        self.assertEqual(1.0, bench_data['id1'][5]['average'])

        self.assertEqual('current_branch', bench_data['id1'][0]['bar_type'])
        self.assertEqual('current_branch', bench_data['id1'][1]['bar_type'])
        self.assertEqual('current_branch', bench_data['id1'][2]['bar_type'])
        self.assertEqual('other_branch', bench_data['id1'][3]['bar_type'])
        self.assertEqual('other_branch', bench_data['id1'][4]['bar_type'])
        self.assertEqual('other_branch', bench_data['id1'][5]['bar_type'])
