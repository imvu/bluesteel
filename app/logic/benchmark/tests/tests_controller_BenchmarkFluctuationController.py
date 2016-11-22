""" Benchmark Fluctuation Controller tests """

from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from app.logic.benchmark.controllers.BenchmarkFluctuationController import BenchmarkFluctuationController
from app.logic.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.logic.benchmark.models.BenchmarkDefinitionWorkerPassModel import BenchmarkDefinitionWorkerPassEntry
from app.logic.benchmark.models.BenchmarkExecutionModel import BenchmarkExecutionEntry
from app.logic.benchmark.models.BenchmarkFluctuationOverrideModel import BenchmarkFluctuationOverrideEntry
from app.logic.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.logic.bluesteel.controllers.BluesteelProjectController import BluesteelProjectController
from app.logic.gitrepo.models.GitProjectModel import GitProjectEntry
from app.logic.gitrepo.models.GitParentModel import GitParentEntry
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
from app.logic.mailing.models.StackedMailModel import StackedMailEntry
from datetime import timedelta
import json

class BenchmarkFluctuationControllerTestCase(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user('user1@test.com', 'user1@test.com', 'pass')
        self.user1.save()

        self.user2 = User.objects.create_user('user2@test.com', 'user2@test.com', 'pass')
        self.user2.save()

        self.git_project1 = GitProjectEntry.objects.create(url='http://test/')

        self.git_user1 = GitUserEntry.objects.create(project=self.git_project1, name='user1', email='user1@test.com')

        self.commit1 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000100001000010000100001000010000100001', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())
        self.commit2 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000200002000020000200002000020000200002', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())
        self.commit3 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000300003000030000300003000030000300003', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())

        self.command_group = CommandGroupEntry.objects.create()
        self.command_set = CommandSetEntry.objects.create(group=self.command_group)

        self.bluesteel_layout = BluesteelLayoutEntry.objects.create(name='Layout', active=True, project_index_path=0,)
        self.bluesteel_project = BluesteelProjectEntry.objects.create(name='Project', order=0, layout=self.bluesteel_layout, command_group=self.command_group, git_project=self.git_project1,)

        self.benchmark_definition1 = BenchmarkDefinitionEntry.objects.create(name='BenchmarkDefinition1', layout=self.bluesteel_layout, project=self.bluesteel_project, active=True, command_set=self.command_set, revision=28,)
        self.benchmark_definition2 = BenchmarkDefinitionEntry.objects.create(name='BenchmarkDefinition2', layout=self.bluesteel_layout, project=self.bluesteel_project, active=True, command_set=self.command_set, revision=3,)

        self.worker1 = WorkerEntry.objects.create(name='worker-name-1', uuid='uuid-worker-1', operative_system='osx', description='long-description-1', user=self.user1, git_feeder=False)
        self.worker2 = WorkerEntry.objects.create(name='worker-name-2', uuid='uuid-worker-2', operative_system='osx', description='long-description-2', user=self.user2, git_feeder=False)

        self.report1 = CommandSetEntry.objects.create(group=None)
        self.report2 = CommandSetEntry.objects.create(group=None)
        self.report3 = CommandSetEntry.objects.create(group=None)

        self.benchmark_execution1 = BenchmarkExecutionEntry.objects.create(definition=self.benchmark_definition1, commit=self.commit1, worker=self.worker1, report=self.report1, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY,)
        self.benchmark_execution2 = BenchmarkExecutionEntry.objects.create(definition=self.benchmark_definition1, commit=self.commit2, worker=self.worker1, report=self.report2, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY,)
        self.benchmark_execution3 = BenchmarkExecutionEntry.objects.create(definition=self.benchmark_definition2, commit=self.commit1, worker=self.worker2, report=self.report3, invalidated=False, revision_target=2, status=BenchmarkExecutionEntry.READY,)

        self.worker_pass11 = BenchmarkDefinitionWorkerPassEntry.objects.create(definition=self.benchmark_definition1, worker=self.worker1)
        self.worker_pass12 = BenchmarkDefinitionWorkerPassEntry.objects.create(definition=self.benchmark_definition1, worker=self.worker2)
        self.worker_pass21 = BenchmarkDefinitionWorkerPassEntry.objects.create(definition=self.benchmark_definition2, worker=self.worker1)
        self.worker_pass22 = BenchmarkDefinitionWorkerPassEntry.objects.create(definition=self.benchmark_definition2, worker=self.worker2)

    def tearDown(self):
        pass

    def test_get_benchmark_fluctuation_same_average(self):
        commit0 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000000000000000000000000000000000000000', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())
        commit1 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000100001000010000100001000010000100001', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())
        commit2 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000200002000020000200002000020000200002', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())
        commit3 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000300003000030000300003000030000300003', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())
        commit4 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000400004000040000400004000040000400004', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())
        commit5 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000500005000050000500005000050000500005', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())

        branch_test = GitBranchEntry.objects.create(project=self.git_project1, name='branch-test', commit=commit5)
        # GitBranchMergeTargetEntry.objects.create(project=self.git_project1, current_branch=branch2, target_branch=self.branch1, fork_point=self.commit3)

        trail0 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch_test, commit=commit0, order=5)
        trail1 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch_test, commit=commit1, order=4)
        trail2 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch_test, commit=commit2, order=3)
        trail3 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch_test, commit=commit3, order=2)
        trail4 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch_test, commit=commit4, order=1)
        trail5 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch_test, commit=commit5, order=0)

        parent0_1 = GitParentEntry.objects.create(project=self.git_project1, parent=commit0, son=commit1, order=0)
        parent1_2 = GitParentEntry.objects.create(project=self.git_project1, parent=commit1, son=commit2, order=1)
        parent2_3 = GitParentEntry.objects.create(project=self.git_project1, parent=commit2, son=commit3, order=2)
        parent3_4 = GitParentEntry.objects.create(project=self.git_project1, parent=commit3, son=commit4, order=3)
        parent4_5 = GitParentEntry.objects.create(project=self.git_project1, parent=commit4, son=commit5, order=4)

        report_0 = CommandSetEntry.objects.create(group=None)
        report_1 = CommandSetEntry.objects.create(group=None)
        report_2 = CommandSetEntry.objects.create(group=None)
        report_3 = CommandSetEntry.objects.create(group=None)
        report_4 = CommandSetEntry.objects.create(group=None)
        report_5 = CommandSetEntry.objects.create(group=None)

        com0_1 = CommandEntry.objects.create(command_set=report_0, command='command0-1', order=0)
        com1_1 = CommandEntry.objects.create(command_set=report_1, command='command1-1', order=1)
        com2_1 = CommandEntry.objects.create(command_set=report_2, command='command2-1', order=2)
        com3_1 = CommandEntry.objects.create(command_set=report_3, command='command3-1', order=3)
        com4_1 = CommandEntry.objects.create(command_set=report_4, command='command4-1', order=4)
        com5_1 = CommandEntry.objects.create(command_set=report_5, command='command5-1', order=5)

        com0_2 = CommandEntry.objects.create(command_set=report_0, command='command0-2', order=0)
        com1_2 = CommandEntry.objects.create(command_set=report_1, command='command1-2', order=1)
        com2_2 = CommandEntry.objects.create(command_set=report_2, command='command2-2', order=2)
        com3_2 = CommandEntry.objects.create(command_set=report_3, command='command3-2', order=3)
        com4_2 = CommandEntry.objects.create(command_set=report_4, command='command4-2', order=4)
        com5_2 = CommandEntry.objects.create(command_set=report_5, command='command5-2', order=5)

        out_0_1 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1,1,2,3,3]}, {'visual_type' : 'vertical_bars', 'id' : 'id2', 'data' : [1,1,2,3,3]}])
        out_1_1 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1,1,2,3,3]}, {'visual_type' : 'vertical_bars', 'id' : 'id2', 'data' : [1,1,2,3,3]}])
        out_2_1 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1,1,2,3,3]}, {'visual_type' : 'vertical_bars', 'id' : 'id2', 'data' : [1,1,2,3,3]}])
        out_3_1 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1,1,2,3,3]}, {'visual_type' : 'vertical_bars', 'id' : 'id2', 'data' : [1,1,2,3,3]}])
        out_4_1 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1,1,2,3,3]}, {'visual_type' : 'vertical_bars', 'id' : 'id2', 'data' : [1,1,2,3,3]}])
        out_5_1 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1,1,2,3,3]}, {'visual_type' : 'vertical_bars', 'id' : 'id2', 'data' : [1,1,2,3,3]}])

        out_0_2 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id3', 'data' : [1,1,2,3,3]}, {'visual_type' : 'vertical_bars', 'id' : 'id4', 'data' : [1,1,2,3,3]}])
        out_1_2 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id3', 'data' : [1,1,2,3,3]}, {'visual_type' : 'vertical_bars', 'id' : 'id4', 'data' : [1,1,2,3,3]}])
        out_2_2 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id3', 'data' : [1,1,2,3,3]}, {'visual_type' : 'vertical_bars', 'id' : 'id4', 'data' : [1,1,2,3,3]}])
        out_3_2 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id3', 'data' : [1,1,2,3,3]}, {'visual_type' : 'vertical_bars', 'id' : 'id4', 'data' : [1,1,2,3,3]}])
        out_4_2 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id3', 'data' : [1,1,2,3,3]}, {'visual_type' : 'vertical_bars', 'id' : 'id4', 'data' : [1,1,2,3,3]}])
        out_5_2 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id3', 'data' : [1,1,2,3,3]}, {'visual_type' : 'vertical_bars', 'id' : 'id4', 'data' : [1,1,2,3,3]}])

        CommandResultEntry.objects.create(command=com0_1, out=out_0_1, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com1_1, out=out_1_1, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com2_1, out=out_2_1, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com3_1, out=out_3_1, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com4_1, out=out_4_1, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com5_1, out=out_5_1, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())

        CommandResultEntry.objects.create(command=com0_2, out=out_0_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com1_2, out=out_1_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com2_2, out=out_2_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com3_2, out=out_3_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com4_2, out=out_4_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com5_2, out=out_5_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())

        benchmark_execution0 = BenchmarkExecutionEntry.objects.create(definition=self.benchmark_definition1, commit=commit0, worker=self.worker1, report=report_0, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)
        benchmark_execution1 = BenchmarkExecutionEntry.objects.create(definition=self.benchmark_definition1, commit=commit1, worker=self.worker1, report=report_1, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)
        benchmark_execution2 = BenchmarkExecutionEntry.objects.create(definition=self.benchmark_definition1, commit=commit2, worker=self.worker1, report=report_2, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)
        benchmark_execution3 = BenchmarkExecutionEntry.objects.create(definition=self.benchmark_definition1, commit=commit3, worker=self.worker1, report=report_3, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)
        benchmark_execution4 = BenchmarkExecutionEntry.objects.create(definition=self.benchmark_definition1, commit=commit4, worker=self.worker1, report=report_4, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)
        benchmark_execution5 = BenchmarkExecutionEntry.objects.create(definition=self.benchmark_definition1, commit=commit5, worker=self.worker1, report=report_5, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)

        fluctuation = BenchmarkFluctuationController.get_benchmark_fluctuation(self.git_project1, self.benchmark_definition1.id, self.worker1.id, commit2.commit_hash, 2)
        fluctuation.sort(key=lambda x: x['id'])

        self.assertEqual(4, len(fluctuation))
        self.assertEqual('id1', fluctuation[0]['id'])
        self.assertEqual(2.0, fluctuation[0]['min'])
        self.assertEqual(2.0, fluctuation[0]['max'])
        self.assertEqual('id2', fluctuation[1]['id'])
        self.assertEqual(2.0, fluctuation[1]['min'])
        self.assertEqual(2.0, fluctuation[1]['max'])
        self.assertEqual('id3', fluctuation[2]['id'])
        self.assertEqual(2.0, fluctuation[2]['min'])
        self.assertEqual(2.0, fluctuation[2]['max'])
        self.assertEqual('id4', fluctuation[3]['id'])
        self.assertEqual(2.0, fluctuation[3]['min'])
        self.assertEqual(2.0, fluctuation[3]['max'])

    def test_get_benchmark_fluctuation_different_average(self):
        commit0 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000000000000000000000000000000000000000', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())
        commit1 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000100001000010000100001000010000100001', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())
        commit2 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000200002000020000200002000020000200002', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())
        commit3 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000300003000030000300003000030000300003', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())
        commit4 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000400004000040000400004000040000400004', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())
        commit5 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000500005000050000500005000050000500005', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())

        branch_test = GitBranchEntry.objects.create(project=self.git_project1, name='branch-test', commit=commit5)
        # GitBranchMergeTargetEntry.objects.create(project=self.git_project1, current_branch=branch2, target_branch=self.branch1, fork_point=self.commit3)

        trail0 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch_test, commit=commit0, order=5)
        trail1 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch_test, commit=commit1, order=4)
        trail2 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch_test, commit=commit2, order=3)
        trail3 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch_test, commit=commit3, order=2)
        trail4 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch_test, commit=commit4, order=1)
        trail5 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch_test, commit=commit5, order=0)

        parent0_1 = GitParentEntry.objects.create(project=self.git_project1, parent=commit0, son=commit1, order=0)
        parent1_2 = GitParentEntry.objects.create(project=self.git_project1, parent=commit1, son=commit2, order=1)
        parent2_3 = GitParentEntry.objects.create(project=self.git_project1, parent=commit2, son=commit3, order=2)
        parent3_4 = GitParentEntry.objects.create(project=self.git_project1, parent=commit3, son=commit4, order=3)
        parent4_5 = GitParentEntry.objects.create(project=self.git_project1, parent=commit4, son=commit5, order=4)

        report_0 = CommandSetEntry.objects.create(group=None)
        report_1 = CommandSetEntry.objects.create(group=None)
        report_2 = CommandSetEntry.objects.create(group=None)
        report_3 = CommandSetEntry.objects.create(group=None)
        report_4 = CommandSetEntry.objects.create(group=None)
        report_5 = CommandSetEntry.objects.create(group=None)

        com0_1 = CommandEntry.objects.create(command_set=report_0, command='command0-1', order=0)
        com1_1 = CommandEntry.objects.create(command_set=report_1, command='command1-1', order=1)
        com2_1 = CommandEntry.objects.create(command_set=report_2, command='command2-1', order=2)
        com3_1 = CommandEntry.objects.create(command_set=report_3, command='command3-1', order=3)
        com4_1 = CommandEntry.objects.create(command_set=report_4, command='command4-1', order=4)
        com5_1 = CommandEntry.objects.create(command_set=report_5, command='command5-1', order=5)

        com0_2 = CommandEntry.objects.create(command_set=report_0, command='command0-2', order=0)
        com1_2 = CommandEntry.objects.create(command_set=report_1, command='command1-2', order=1)
        com2_2 = CommandEntry.objects.create(command_set=report_2, command='command2-2', order=2)
        com3_2 = CommandEntry.objects.create(command_set=report_3, command='command3-2', order=3)
        com4_2 = CommandEntry.objects.create(command_set=report_4, command='command4-2', order=4)
        com5_2 = CommandEntry.objects.create(command_set=report_5, command='command5-2', order=5)

        out_0_1 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1,1,2,3,3]}, {'visual_type' : 'vertical_bars', 'id' : 'id2', 'data' : [1,1,2,3,3]}])
        out_1_1 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1,1,2,3,3]}, {'visual_type' : 'vertical_bars', 'id' : 'id2', 'data' : [1,1,2,3,3]}])
        out_2_1 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1,1,2,3,3]}, {'visual_type' : 'vertical_bars', 'id' : 'id2', 'data' : [1,1,2,3,3]}])
        out_3_1 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1,1,2,3,3]}, {'visual_type' : 'vertical_bars', 'id' : 'id2', 'data' : [1,1,2,3,3]}])
        out_4_1 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [3,3,4,5,5]}, {'visual_type' : 'vertical_bars', 'id' : 'id2', 'data' : [4,4,5,6,6]}])
        out_5_1 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1,1,2,3,3]}, {'visual_type' : 'vertical_bars', 'id' : 'id2', 'data' : [1,1,2,3,3]}])

        out_0_2 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id3', 'data' : [1,1,2,3,3]}, {'visual_type' : 'vertical_bars', 'id' : 'id4', 'data' : [1,1,2,3,3]}])
        out_1_2 = json.dumps([                                                                       {'visual_type' : 'vertical_bars', 'id' : 'id4', 'data' : [1,1,2,3,3]}])
        out_2_2 = json.dumps([                                                                       {'visual_type' : 'vertical_bars', 'id' : 'id4', 'data' : [1,1,2,3,3]}])
        out_3_2 = json.dumps([                                                                       {'visual_type' : 'vertical_bars', 'id' : 'id4', 'data' : [1,1,2,3,3]}])
        out_4_2 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id3', 'data' : [4,4,5,6,6]}, {'visual_type' : 'vertical_bars', 'id' : 'id4', 'data' : [7,7,8,9,9]}])
        out_5_2 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id3', 'data' : [1,1,2,3,3]}, {'visual_type' : 'vertical_bars', 'id' : 'id4', 'data' : [1,1,2,3,3]}])

        CommandResultEntry.objects.create(command=com0_1, out=out_0_1, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com1_1, out=out_1_1, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com2_1, out=out_2_1, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com3_1, out=out_3_1, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com4_1, out=out_4_1, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com5_1, out=out_5_1, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())

        CommandResultEntry.objects.create(command=com0_2, out=out_0_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com1_2, out=out_1_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com2_2, out=out_2_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com3_2, out=out_3_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com4_2, out=out_4_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com5_2, out=out_5_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())

        benchmark_execution0 = BenchmarkExecutionEntry.objects.create(definition=self.benchmark_definition1, commit=commit0, worker=self.worker1, report=report_0, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)
        benchmark_execution1 = BenchmarkExecutionEntry.objects.create(definition=self.benchmark_definition1, commit=commit1, worker=self.worker1, report=report_1, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)
        benchmark_execution2 = BenchmarkExecutionEntry.objects.create(definition=self.benchmark_definition1, commit=commit2, worker=self.worker1, report=report_2, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)
        benchmark_execution3 = BenchmarkExecutionEntry.objects.create(definition=self.benchmark_definition1, commit=commit3, worker=self.worker1, report=report_3, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)
        benchmark_execution4 = BenchmarkExecutionEntry.objects.create(definition=self.benchmark_definition1, commit=commit4, worker=self.worker1, report=report_4, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)
        benchmark_execution5 = BenchmarkExecutionEntry.objects.create(definition=self.benchmark_definition1, commit=commit5, worker=self.worker1, report=report_5, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)

        fluctuation = BenchmarkFluctuationController.get_benchmark_fluctuation(self.git_project1, self.benchmark_definition1.id, self.worker1.id, commit2.commit_hash, 2)
        fluctuation.sort(key=lambda x: x['id'])

        self.assertEqual(4, len(fluctuation))
        self.assertEqual('id1', fluctuation[0]['id'])
        self.assertEqual(2.0, fluctuation[0]['min'])
        self.assertEqual(4.0, fluctuation[0]['max'])
        self.assertEqual('id2', fluctuation[1]['id'])
        self.assertEqual(2.0, fluctuation[1]['min'])
        self.assertEqual(5.0, fluctuation[1]['max'])
        self.assertEqual('id3', fluctuation[2]['id'])
        self.assertEqual(2.0, fluctuation[2]['min'])
        self.assertEqual(5.0, fluctuation[2]['max'])
        self.assertEqual('id4', fluctuation[3]['id'])
        self.assertEqual(2.0, fluctuation[3]['min'])
        self.assertEqual(8.0, fluctuation[3]['max'])

    def test_get_benchmark_fluctuation_among_others(self):
        self.benchmark_execution1.delete()
        self.benchmark_execution2.delete()
        self.benchmark_execution3.delete()

        commit0 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000000000000000000000000000000000000000', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())
        commit1 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000100001000010000100001000010000100001', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())

        branch_test = GitBranchEntry.objects.create(project=self.git_project1, name='branch-test', commit=commit1)

        trail0 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch_test, commit=commit0, order=5)
        trail1 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch_test, commit=commit1, order=4)

        parent0_1 = GitParentEntry.objects.create(project=self.git_project1, parent=commit0, son=commit1, order=0)

        # First group of Benchmark Executions
        report_0_0 = CommandSetEntry.objects.create(group=None)
        report_0_1 = CommandSetEntry.objects.create(group=None)

        com0_0 = CommandEntry.objects.create(command_set=report_0_0, command='command0-0', order=0)
        com0_1 = CommandEntry.objects.create(command_set=report_0_1, command='command0-1', order=1)

        out_0_0 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1,1,2,3,3]}, {'visual_type' : 'vertical_bars', 'id' : 'id2', 'data' : [1,1,3,5,4]}])
        out_0_1 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1,1,3,6,6]}, {'visual_type' : 'vertical_bars', 'id' : 'id2', 'data' : [1,1,3,5,5]}])

        CommandResultEntry.objects.create(command=com0_0, out=out_0_0, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com0_1, out=out_0_1, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())

        benchmark_execution0 = BenchmarkExecutionEntry.objects.create(definition=self.benchmark_definition1, commit=commit0, worker=self.worker1, report=report_0_0, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)
        benchmark_execution1 = BenchmarkExecutionEntry.objects.create(definition=self.benchmark_definition1, commit=commit1, worker=self.worker1, report=report_0_1, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)

        # Second group of Benchmark Executions
        report_1_0 = CommandSetEntry.objects.create(group=None)
        report_1_1 = CommandSetEntry.objects.create(group=None)

        com1_0 = CommandEntry.objects.create(command_set=report_1_0, command='command1-0', order=0)
        com1_1 = CommandEntry.objects.create(command_set=report_1_1, command='command1-1', order=1)

        out_1_0 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1,1,2,3,3]}, {'visual_type' : 'vertical_bars', 'id' : 'id2', 'data' : [1,1,3,4,4]}])
        out_1_1 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1,1,3,7,7]}, {'visual_type' : 'vertical_bars', 'id' : 'id2', 'data' : [1,1,4,8,8]}])

        CommandResultEntry.objects.create(command=com1_0, out=out_1_0, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com1_1, out=out_1_1, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())

        benchmark_execution2 = BenchmarkExecutionEntry.objects.create(definition=self.benchmark_definition2, commit=commit0, worker=self.worker2, report=report_1_0, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)
        benchmark_execution3 = BenchmarkExecutionEntry.objects.create(definition=self.benchmark_definition2, commit=commit1, worker=self.worker2, report=report_1_1, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)

        fluctuation1 = BenchmarkFluctuationController.get_benchmark_fluctuation(self.git_project1, self.benchmark_definition1.id, self.worker1.id, commit0.commit_hash, 2)
        fluctuation1.sort(key=lambda x: x['id'])

        self.assertEqual(2, len(fluctuation1))
        self.assertEqual('id1', fluctuation1[0]['id'])
        self.assertEqual(2.0, fluctuation1[0]['min'])
        self.assertEqual(3.0, fluctuation1[0]['max'])
        self.assertEqual('id2', fluctuation1[1]['id'])
        self.assertEqual(3.0, fluctuation1[1]['min'])
        self.assertEqual(3.0, fluctuation1[1]['max'])

        fluctuation2 = BenchmarkFluctuationController.get_benchmark_fluctuation(self.git_project1, self.benchmark_definition2.id, self.worker2.id, commit0.commit_hash, 2)
        fluctuation2.sort(key=lambda x: x['id'])

        self.assertEqual(2, len(fluctuation2))
        self.assertEqual('id1', fluctuation2[0]['id'])
        self.assertEqual(2.0, fluctuation2[0]['min'])
        self.assertEqual(3.0, fluctuation2[0]['max'])
        self.assertEqual('id2', fluctuation2[1]['id'])
        self.assertEqual(3.0, fluctuation2[1]['min'])
        self.assertEqual(4.0, fluctuation2[1]['max'])


    def test_does_benchmark_fluctuation_exist(self):
        self.benchmark_definition1.max_fluctuation_percent = 49
        self.benchmark_definition1.save()

        commit0 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000000000000000000000000000000000000000', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())
        commit1 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000100001000010000100001000010000100001', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())
        commit2 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000200002000020000200002000020000200002', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())
        commit3 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000300003000030000300003000030000300003', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())
        commit4 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000400004000040000400004000040000400004', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())
        commit5 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000500005000050000500005000050000500005', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())

        branch_test = GitBranchEntry.objects.create(project=self.git_project1, name='branch-test', commit=commit5)
        # GitBranchMergeTargetEntry.objects.create(project=self.git_project1, current_branch=branch2, target_branch=self.branch1, fork_point=self.commit3)

        trail0 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch_test, commit=commit0, order=5)
        trail1 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch_test, commit=commit1, order=4)
        trail2 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch_test, commit=commit2, order=3)
        trail3 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch_test, commit=commit3, order=2)
        trail4 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch_test, commit=commit4, order=1)
        trail5 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch_test, commit=commit5, order=0)

        parent0_1 = GitParentEntry.objects.create(project=self.git_project1, parent=commit0, son=commit1, order=0)
        parent1_2 = GitParentEntry.objects.create(project=self.git_project1, parent=commit1, son=commit2, order=1)
        parent2_3 = GitParentEntry.objects.create(project=self.git_project1, parent=commit2, son=commit3, order=2)
        parent3_4 = GitParentEntry.objects.create(project=self.git_project1, parent=commit3, son=commit4, order=3)
        parent4_5 = GitParentEntry.objects.create(project=self.git_project1, parent=commit4, son=commit5, order=4)

        report_0 = CommandSetEntry.objects.create(group=None)
        report_1 = CommandSetEntry.objects.create(group=None)
        report_2 = CommandSetEntry.objects.create(group=None)
        report_3 = CommandSetEntry.objects.create(group=None)
        report_4 = CommandSetEntry.objects.create(group=None)
        report_5 = CommandSetEntry.objects.create(group=None)

        com0_1 = CommandEntry.objects.create(command_set=report_0, command='command0-1', order=0)
        com1_1 = CommandEntry.objects.create(command_set=report_1, command='command1-1', order=1)
        com2_1 = CommandEntry.objects.create(command_set=report_2, command='command2-1', order=2)
        com3_1 = CommandEntry.objects.create(command_set=report_3, command='command3-1', order=3)
        com4_1 = CommandEntry.objects.create(command_set=report_4, command='command4-1', order=4)
        com5_1 = CommandEntry.objects.create(command_set=report_5, command='command5-1', order=5)

        com0_2 = CommandEntry.objects.create(command_set=report_0, command='command0-2', order=0)
        com1_2 = CommandEntry.objects.create(command_set=report_1, command='command1-2', order=1)
        com2_2 = CommandEntry.objects.create(command_set=report_2, command='command2-2', order=2)
        com3_2 = CommandEntry.objects.create(command_set=report_3, command='command3-2', order=3)
        com4_2 = CommandEntry.objects.create(command_set=report_4, command='command4-2', order=4)
        com5_2 = CommandEntry.objects.create(command_set=report_5, command='command5-2', order=5)

        out_0_1 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1.0, 1.0, 1.0, 1.0, 1.0]}, {'visual_type' : 'vertical_bars', 'id' : 'id2', 'data' : [1,1,1,1,1]}])
        out_1_1 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1.0, 1.0, 1.0, 1.0, 1.0]}, {'visual_type' : 'vertical_bars', 'id' : 'id2', 'data' : [1,1,1,1,1]}])
        out_2_1 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1.0, 1.0, 1.0, 1.0, 1.0]}, {'visual_type' : 'vertical_bars', 'id' : 'id2', 'data' : [1,1,1,1,1]}])
        out_3_1 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1.0, 1.0, 1.0, 1.0, 1.0]}, {'visual_type' : 'vertical_bars', 'id' : 'id2', 'data' : [1,1,1,1,1]}])
        out_4_1 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1.0, 1.0, 1.0, 1.0, 1.0]}, {'visual_type' : 'vertical_bars', 'id' : 'id2', 'data' : [1,1,1,1,1]}])
        out_5_1 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1.5, 1.5, 1.5, 1.5, 1.5]}, {'visual_type' : 'vertical_bars', 'id' : 'id2', 'data' : [1,1,1,1,1]}])

        out_0_2 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id3', 'data' : [1,1,1,1,1]}, {'visual_type' : 'vertical_bars', 'id' : 'id4', 'data' : [1,1,1,1,1]}])
        out_1_2 = json.dumps([                                                                       {'visual_type' : 'vertical_bars', 'id' : 'id4', 'data' : [1,1,1,1,1]}])
        out_2_2 = json.dumps([                                                                       {'visual_type' : 'vertical_bars', 'id' : 'id4', 'data' : [1,1,1,1,1]}])
        out_3_2 = json.dumps([                                                                       {'visual_type' : 'vertical_bars', 'id' : 'id4', 'data' : [1,1,1,1,1]}])
        out_4_2 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id3', 'data' : [1,1,1,1,1]}, {'visual_type' : 'vertical_bars', 'id' : 'id4', 'data' : [1,1,1,1,1]}])
        out_5_2 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id3', 'data' : [1,1,1,1,1]}, {'visual_type' : 'vertical_bars', 'id' : 'id4', 'data' : [1,1,1,1,1]}])

        CommandResultEntry.objects.create(command=com0_1, out=out_0_1, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com1_1, out=out_1_1, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com2_1, out=out_2_1, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com3_1, out=out_3_1, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com4_1, out=out_4_1, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com5_1, out=out_5_1, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())

        CommandResultEntry.objects.create(command=com0_2, out=out_0_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com1_2, out=out_1_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com2_2, out=out_2_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com3_2, out=out_3_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com4_2, out=out_4_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com5_2, out=out_5_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())

        benchmark_execution0 = BenchmarkExecutionEntry.objects.create(definition=self.benchmark_definition1, commit=commit0, worker=self.worker1, report=report_0, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)
        benchmark_execution1 = BenchmarkExecutionEntry.objects.create(definition=self.benchmark_definition1, commit=commit1, worker=self.worker1, report=report_1, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)
        benchmark_execution2 = BenchmarkExecutionEntry.objects.create(definition=self.benchmark_definition1, commit=commit2, worker=self.worker1, report=report_2, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)
        benchmark_execution3 = BenchmarkExecutionEntry.objects.create(definition=self.benchmark_definition1, commit=commit3, worker=self.worker1, report=report_3, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)
        benchmark_execution4 = BenchmarkExecutionEntry.objects.create(definition=self.benchmark_definition1, commit=commit4, worker=self.worker1, report=report_4, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)
        benchmark_execution5 = BenchmarkExecutionEntry.objects.create(definition=self.benchmark_definition1, commit=commit5, worker=self.worker1, report=report_5, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)

        self.assertFalse(BenchmarkFluctuationController.does_benchmark_fluctuation_exist(benchmark_execution0, 1)[0])
        self.assertFalse(BenchmarkFluctuationController.does_benchmark_fluctuation_exist(benchmark_execution1, 1)[0])
        self.assertFalse(BenchmarkFluctuationController.does_benchmark_fluctuation_exist(benchmark_execution2, 1)[0])
        self.assertFalse(BenchmarkFluctuationController.does_benchmark_fluctuation_exist(benchmark_execution3, 1)[0])

        flucs1 = BenchmarkFluctuationController.does_benchmark_fluctuation_exist(benchmark_execution4, 1)
        self.assertTrue(flucs1[0])
        self.assertEqual(1, len(flucs1[1]))
        self.assertEqual('id1', flucs1[1][0]['id'])
        self.assertEqual(1.0, flucs1[1][0]['min'])
        self.assertEqual(1.5, flucs1[1][0]['max'])

        flucs2 = BenchmarkFluctuationController.does_benchmark_fluctuation_exist(benchmark_execution5, 1)
        self.assertTrue(flucs2[0])
        self.assertEqual(1, len(flucs2[1]))
        self.assertEqual('id1', flucs2[1][0]['id'])
        self.assertEqual(1.0, flucs2[1][0]['min'])
        self.assertEqual(1.5, flucs2[1][0]['max'])

    def test_get_benchmark_fluctuation_on_parent_and_son(self):
        self.commit1.delete()
        self.commit2.delete()
        self.commit3.delete()

        commit0 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000000000000000000000000000000000000000', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())
        commit1 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000100001000010000100001000010000100001', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())
        commit2 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000200002000020000200002000020000200002', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())
        commit3 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000300003000030000300003000030000300003', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())
        commit4 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000400004000040000400004000040000400004', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())
        commit5 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000500005000050000500005000050000500005', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())

        branch_test = GitBranchEntry.objects.create(project=self.git_project1, name='branch-test', commit=commit5)
        # GitBranchMergeTargetEntry.objects.create(project=self.git_project1, current_branch=branch2, target_branch=self.branch1, fork_point=self.commit3)

        trail0 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch_test, commit=commit0, order=5)
        trail1 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch_test, commit=commit1, order=4)
        trail2 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch_test, commit=commit2, order=3)
        trail3 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch_test, commit=commit3, order=2)
        trail4 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch_test, commit=commit4, order=1)
        trail5 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch_test, commit=commit5, order=0)

        parent0_1 = GitParentEntry.objects.create(project=self.git_project1, parent=commit0, son=commit1, order=0)
        parent1_2 = GitParentEntry.objects.create(project=self.git_project1, parent=commit1, son=commit2, order=1)
        parent2_3 = GitParentEntry.objects.create(project=self.git_project1, parent=commit2, son=commit3, order=2)
        parent3_4 = GitParentEntry.objects.create(project=self.git_project1, parent=commit3, son=commit4, order=3)
        parent4_5 = GitParentEntry.objects.create(project=self.git_project1, parent=commit4, son=commit5, order=4)

        report_0 = CommandSetEntry.objects.create(group=None)
        report_1 = CommandSetEntry.objects.create(group=None)
        report_2 = CommandSetEntry.objects.create(group=None)
        report_3 = CommandSetEntry.objects.create(group=None)
        report_4 = CommandSetEntry.objects.create(group=None)
        report_5 = CommandSetEntry.objects.create(group=None)

        com0_1 = CommandEntry.objects.create(command_set=report_0, command='command0-1', order=0)
        com1_1 = CommandEntry.objects.create(command_set=report_1, command='command1-1', order=1)
        com2_1 = CommandEntry.objects.create(command_set=report_2, command='command2-1', order=2)
        com3_1 = CommandEntry.objects.create(command_set=report_3, command='command3-1', order=3)
        com4_1 = CommandEntry.objects.create(command_set=report_4, command='command4-1', order=4)
        com5_1 = CommandEntry.objects.create(command_set=report_5, command='command5-1', order=5)

        com0_2 = CommandEntry.objects.create(command_set=report_0, command='command0-2', order=0)
        com1_2 = CommandEntry.objects.create(command_set=report_1, command='command1-2', order=1)
        com2_2 = CommandEntry.objects.create(command_set=report_2, command='command2-2', order=2)
        com3_2 = CommandEntry.objects.create(command_set=report_3, command='command3-2', order=3)
        com4_2 = CommandEntry.objects.create(command_set=report_4, command='command4-2', order=4)
        com5_2 = CommandEntry.objects.create(command_set=report_5, command='command5-2', order=5)

        out_0_1 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1,1,2,3,3]}, {'visual_type' : 'vertical_bars', 'id' : 'id2', 'data' : [1,1,2,3,3]}])
        out_1_1 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1,1,2,3,3]}, {'visual_type' : 'vertical_bars', 'id' : 'id2', 'data' : [1,1,2,3,3]}])
        out_2_1 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1,1,2,3,3]}, {'visual_type' : 'vertical_bars', 'id' : 'id2', 'data' : [1,1,2,3,3]}])
        out_3_1 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1,1,2,3,3]}, {'visual_type' : 'vertical_bars', 'id' : 'id2', 'data' : [1,1,2,3,3]}])
        out_4_1 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [3,3,4,5,5]}, {'visual_type' : 'vertical_bars', 'id' : 'id2', 'data' : [4,4,5,6,6]}])
        out_5_1 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1,1,2,3,3]}, {'visual_type' : 'vertical_bars', 'id' : 'id2', 'data' : [1,1,2,3,3]}])

        out_0_2 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id3', 'data' : [1,1,2,3,3]}, {'visual_type' : 'vertical_bars', 'id' : 'id4', 'data' : [1,1,2,3,3]}])
        out_1_2 = json.dumps([                                                                       {'visual_type' : 'vertical_bars', 'id' : 'id4', 'data' : [1,1,2,3,3]}])
        out_2_2 = json.dumps([                                                                       {'visual_type' : 'vertical_bars', 'id' : 'id4', 'data' : [1,1,2,3,3]}])
        out_3_2 = json.dumps([                                                                       {'visual_type' : 'vertical_bars', 'id' : 'id4', 'data' : [1,1,2,3,3]}])
        out_4_2 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id3', 'data' : [4,4,5,6,6]}, {'visual_type' : 'vertical_bars', 'id' : 'id4', 'data' : [7,7,8,9,9]}])
        out_5_2 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id3', 'data' : [1,1,2,3,3]}, {'visual_type' : 'vertical_bars', 'id' : 'id4', 'data' : [1,1,2,3,3]}])

        CommandResultEntry.objects.create(command=com0_1, out=out_0_1, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com1_1, out=out_1_1, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com2_1, out=out_2_1, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com3_1, out=out_3_1, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com4_1, out=out_4_1, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com5_1, out=out_5_1, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())

        CommandResultEntry.objects.create(command=com0_2, out=out_0_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com1_2, out=out_1_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com2_2, out=out_2_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com3_2, out=out_3_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com4_2, out=out_4_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com5_2, out=out_5_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())

        benchmark_execution0 = BenchmarkExecutionEntry.objects.create(definition=self.benchmark_definition1, commit=commit0, worker=self.worker1, report=report_0, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)
        benchmark_execution1 = BenchmarkExecutionEntry.objects.create(definition=self.benchmark_definition1, commit=commit1, worker=self.worker1, report=report_1, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)
        benchmark_execution2 = BenchmarkExecutionEntry.objects.create(definition=self.benchmark_definition1, commit=commit2, worker=self.worker1, report=report_2, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)
        benchmark_execution3 = BenchmarkExecutionEntry.objects.create(definition=self.benchmark_definition1, commit=commit3, worker=self.worker1, report=report_3, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)
        benchmark_execution4 = BenchmarkExecutionEntry.objects.create(definition=self.benchmark_definition1, commit=commit4, worker=self.worker1, report=report_4, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)
        benchmark_execution5 = BenchmarkExecutionEntry.objects.create(definition=self.benchmark_definition1, commit=commit5, worker=self.worker1, report=report_5, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)

        fluctuation = BenchmarkFluctuationController.get_benchmark_fluctuation_adjacent(self.git_project1, self.benchmark_definition1.id, self.worker1.id, commit2.commit_hash)

        self.assertEqual(2.0, fluctuation['id1']['parent']['median'])
        self.assertEqual(2.0, fluctuation['id1']['current']['median'])
        self.assertEqual(2.0, fluctuation['id1']['son']['median'])
        self.assertEqual(True, fluctuation['id1']['parent']['has_results'])
        self.assertEqual(True, fluctuation['id1']['current']['has_results'])
        self.assertEqual(True, fluctuation['id1']['son']['has_results'])
        self.assertEqual('0000100001000010000100001000010000100001', fluctuation['id1']['parent']['commit_hash'])
        self.assertEqual('0000200002000020000200002000020000200002', fluctuation['id1']['current']['commit_hash'])
        self.assertEqual('0000300003000030000300003000030000300003', fluctuation['id1']['son']['commit_hash'])

        self.assertEqual(2.0, fluctuation['id2']['parent']['median'])
        self.assertEqual(2.0, fluctuation['id2']['current']['median'])
        self.assertEqual(2.0, fluctuation['id2']['son']['median'])
        self.assertEqual(True, fluctuation['id2']['parent']['has_results'])
        self.assertEqual(True, fluctuation['id2']['current']['has_results'])
        self.assertEqual(True, fluctuation['id2']['son']['has_results'])
        self.assertEqual('0000100001000010000100001000010000100001', fluctuation['id2']['parent']['commit_hash'])
        self.assertEqual('0000200002000020000200002000020000200002', fluctuation['id2']['current']['commit_hash'])
        self.assertEqual('0000300003000030000300003000030000300003', fluctuation['id2']['son']['commit_hash'])

        self.assertTrue('id3' not in fluctuation)

        self.assertEqual(2.0, fluctuation['id4']['parent']['median'])
        self.assertEqual(2.0, fluctuation['id4']['current']['median'])
        self.assertEqual(2.0, fluctuation['id4']['son']['median'])
        self.assertEqual(True, fluctuation['id4']['parent']['has_results'])
        self.assertEqual(True, fluctuation['id4']['current']['has_results'])
        self.assertEqual(True, fluctuation['id4']['son']['has_results'])
        self.assertEqual('0000100001000010000100001000010000100001', fluctuation['id4']['parent']['commit_hash'])
        self.assertEqual('0000200002000020000200002000020000200002', fluctuation['id4']['current']['commit_hash'])
        self.assertEqual('0000300003000030000300003000030000300003', fluctuation['id4']['son']['commit_hash'])

        fluctuation = BenchmarkFluctuationController.get_benchmark_fluctuation_adjacent(self.git_project1, self.benchmark_definition1.id, self.worker1.id, commit3.commit_hash)

        self.assertEqual(2.0, fluctuation['id1']['parent']['median'])
        self.assertEqual(2.0, fluctuation['id1']['current']['median'])
        self.assertEqual(4.0, fluctuation['id1']['son']['median'])
        self.assertEqual(True, fluctuation['id1']['parent']['has_results'])
        self.assertEqual(True, fluctuation['id1']['current']['has_results'])
        self.assertEqual(True, fluctuation['id1']['son']['has_results'])
        self.assertEqual('0000200002000020000200002000020000200002', fluctuation['id1']['parent']['commit_hash'])
        self.assertEqual('0000300003000030000300003000030000300003', fluctuation['id1']['current']['commit_hash'])
        self.assertEqual('0000400004000040000400004000040000400004', fluctuation['id1']['son']['commit_hash'])

        self.assertEqual(2.0, fluctuation['id2']['parent']['median'])
        self.assertEqual(2.0, fluctuation['id2']['current']['median'])
        self.assertEqual(5.0, fluctuation['id2']['son']['median'])
        self.assertEqual(True, fluctuation['id2']['parent']['has_results'])
        self.assertEqual(True, fluctuation['id2']['current']['has_results'])
        self.assertEqual(True, fluctuation['id2']['son']['has_results'])
        self.assertEqual('0000200002000020000200002000020000200002', fluctuation['id2']['parent']['commit_hash'])
        self.assertEqual('0000300003000030000300003000030000300003', fluctuation['id2']['current']['commit_hash'])
        self.assertEqual('0000400004000040000400004000040000400004', fluctuation['id2']['son']['commit_hash'])

        self.assertEqual(0,   fluctuation['id3']['parent']['median'])
        self.assertEqual(0,   fluctuation['id3']['current']['median'])
        self.assertEqual(5.0, fluctuation['id3']['son']['median'])
        self.assertEqual(False, fluctuation['id3']['parent']['has_results'])
        self.assertEqual(False, fluctuation['id3']['current']['has_results'])
        self.assertEqual(True, fluctuation['id3']['son']['has_results'])
        self.assertEqual('', fluctuation['id3']['parent']['commit_hash'])
        self.assertEqual('', fluctuation['id3']['current']['commit_hash'])
        self.assertEqual('0000400004000040000400004000040000400004', fluctuation['id3']['son']['commit_hash'])

        self.assertEqual(2.0, fluctuation['id4']['parent']['median'])
        self.assertEqual(2.0, fluctuation['id4']['current']['median'])
        self.assertEqual(8.0, fluctuation['id4']['son']['median'])
        self.assertEqual(True, fluctuation['id4']['parent']['has_results'])
        self.assertEqual(True, fluctuation['id4']['current']['has_results'])
        self.assertEqual(True, fluctuation['id4']['son']['has_results'])
        self.assertEqual('0000200002000020000200002000020000200002', fluctuation['id4']['parent']['commit_hash'])
        self.assertEqual('0000300003000030000300003000030000300003', fluctuation['id4']['current']['commit_hash'])
        self.assertEqual('0000400004000040000400004000040000400004', fluctuation['id4']['son']['commit_hash'])


    def test_get_fluctuation_overrides(self):
        fluc_override_1 = BenchmarkFluctuationOverrideEntry.objects.create(definition=self.benchmark_definition1, result_id='id1', override_value=28)
        fluc_override_2 = BenchmarkFluctuationOverrideEntry.objects.create(definition=self.benchmark_definition1, result_id='id2', override_value=29)
        fluc_override_3 = BenchmarkFluctuationOverrideEntry.objects.create(definition=self.benchmark_definition1, result_id='id3', override_value=30)

        ret = BenchmarkFluctuationController.get_fluctuation_overrides(self.benchmark_definition1.id)

        self.assertEqual(3, len(ret))

        self.assertTrue('id1' in ret)
        self.assertTrue('id2' in ret)
        self.assertTrue('id3' in ret)

        self.assertEqual(0.28, ret['id1'])
        self.assertEqual(0.29, ret['id2'])
        self.assertEqual(0.30, ret['id3'])


    def test_get_fluctuation_with_overrides_applied(self):
        max_fluctuation = 0.4

        fluc_overrides = {}
        fluc_overrides['id2'] = 0.75
        fluc_overrides['id4'] = 0.28

        fluc_1 = {'id' : 'id1', 'min' : 1.0, 'max' : 1.5}
        fluc_2 = {'id' : 'id2', 'min' : 1.0, 'max' : 1.5}
        fluc_3 = {'id' : 'id3', 'min' : 1.0, 'max' : 1.5}
        fluc_4 = {'id' : 'id4', 'min' : 1.0, 'max' : 1.5}
        fluc_5 = {'id' : 'id5', 'min' : 1.0, 'max' : 3.5}

        fluctuations = [fluc_1, fluc_2, fluc_3, fluc_4, fluc_5]

        flucs = BenchmarkFluctuationController.get_fluctuations_with_overrides_applied(fluctuations, max_fluctuation, fluc_overrides)
        self.assertTrue(flucs[0])

        fluc_res = flucs[1]
        fluc_res.sort(key=lambda x: x['id'])

        self.assertEqual('id1', fluc_res[0]['id'])
        self.assertEqual('id3', fluc_res[1]['id'])
        self.assertEqual('id4', fluc_res[2]['id'])
        self.assertEqual('id5', fluc_res[3]['id'])

        self.assertEqual(1.0, fluc_res[0]['min'])
        self.assertEqual(1.0, fluc_res[1]['min'])
        self.assertEqual(1.0, fluc_res[2]['min'])
        self.assertEqual(1.0, fluc_res[3]['min'])

        self.assertEqual(1.5, fluc_res[0]['max'])
        self.assertEqual(1.5, fluc_res[1]['max'])
        self.assertEqual(1.5, fluc_res[2]['max'])
        self.assertEqual(3.5, fluc_res[3]['max'])

        self.assertEqual(0.4, fluc_res[0]['max_fluctuation_applied'])
        self.assertEqual(0.4, fluc_res[1]['max_fluctuation_applied'])
        self.assertEqual(0.28, fluc_res[2]['max_fluctuation_applied'])
        self.assertEqual(0.4, fluc_res[3]['max_fluctuation_applied'])
