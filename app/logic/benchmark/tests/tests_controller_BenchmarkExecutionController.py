""" BenchmarkExecution Controller tests """

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
from app.logic.gitrepo.models.GitParentModel import GitParentEntry
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
from app.logic.mailing.models.StackedMailModel import StackedMailEntry
from django.utils import timezone
import json

class BenchmarkExecutionControllerTestCase(TestCase):

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

        self.report1 = CommandSetEntry.objects.create(group=None)
        self.report2 = CommandSetEntry.objects.create(group=None)
        self.report3 = CommandSetEntry.objects.create(group=None)

        self.benchmark_execution1 = BenchmarkExecutionEntry.objects.create(
            definition=self.benchmark_definition1,
            commit=self.commit1,
            worker=self.worker1,
            report=self.report1,
            invalidated=False,
            revision_target=28,
            status=BenchmarkExecutionEntry.READY,
        )

        self.benchmark_execution2 = BenchmarkExecutionEntry.objects.create(
            definition=self.benchmark_definition1,
            commit=self.commit2,
            worker=self.worker1,
            report=self.report2,
            invalidated=False,
            revision_target=28,
            status=BenchmarkExecutionEntry.READY,
        )

        self.benchmark_execution3 = BenchmarkExecutionEntry.objects.create(
            definition=self.benchmark_definition2,
            commit=self.commit1,
            worker=self.worker2,
            report=self.report3,
            invalidated=False,
            revision_target=2,
            status=BenchmarkExecutionEntry.READY,
        )

    def tearDown(self):
        pass

    def test_earliest_available_execution_of_user_1_is_execution_2(self):
        execution = BenchmarkExecutionController.get_earliest_available_execution(self.user1)

        self.assertNotEqual(None, execution)
        self.assertEqual(BenchmarkExecutionEntry.IN_PROGRESS, execution.status)
        self.assertEqual(False, execution.invalidated)
        self.assertEqual(28, self.benchmark_definition1.revision)
        self.assertEqual(28, execution.revision_target)
        self.assertEqual('BenchmarkDefinition1', execution.definition.name)
        self.assertEqual('0000200002000020000200002000020000200002', execution.commit.commit_hash)
        self.assertEqual('worker-name-1', execution.worker.name)

    def test_two_executions_available_of_user_1_are_execution_2_and_then_1(self):
        execution = BenchmarkExecutionController.get_earliest_available_execution(self.user1)

        self.assertNotEqual(None, execution)
        self.assertEqual(BenchmarkExecutionEntry.IN_PROGRESS, execution.status)
        self.assertEqual(False, execution.invalidated)
        self.assertEqual(28, self.benchmark_definition1.revision)
        self.assertEqual(28, execution.revision_target)
        self.assertEqual('BenchmarkDefinition1', execution.definition.name)
        self.assertEqual('0000200002000020000200002000020000200002', execution.commit.commit_hash)
        self.assertEqual('worker-name-1', execution.worker.name)

        execution = BenchmarkExecutionController.get_earliest_available_execution(self.user1)

        self.assertNotEqual(None, execution)
        self.assertEqual(BenchmarkExecutionEntry.IN_PROGRESS, execution.status)
        self.assertEqual(False, execution.invalidated)
        self.assertEqual(28, self.benchmark_definition1.revision)
        self.assertEqual(28, execution.revision_target)
        self.assertEqual('BenchmarkDefinition1', execution.definition.name)
        self.assertEqual('0000100001000010000100001000010000100001', execution.commit.commit_hash)
        self.assertEqual('worker-name-1', execution.worker.name)

    def test_executions_available_ordered_by_commit_creation_time(self):
        self.commit2.author_date = timezone.now()
        self.commit2.save()
        self.commit1.author_date = timezone.now()
        self.commit1.save()

        execution = BenchmarkExecutionController.get_earliest_available_execution(self.user1)

        self.assertNotEqual(None, execution)
        self.assertEqual(BenchmarkExecutionEntry.IN_PROGRESS, execution.status)
        self.assertEqual(False, execution.invalidated)
        self.assertEqual(28, self.benchmark_definition1.revision)
        self.assertEqual(28, execution.revision_target)
        self.assertEqual('BenchmarkDefinition1', execution.definition.name)
        self.assertEqual('0000100001000010000100001000010000100001', execution.commit.commit_hash)
        self.assertEqual('worker-name-1', execution.worker.name)

        execution = BenchmarkExecutionController.get_earliest_available_execution(self.user1)

        self.assertNotEqual(None, execution)
        self.assertEqual(BenchmarkExecutionEntry.IN_PROGRESS, execution.status)
        self.assertEqual(False, execution.invalidated)
        self.assertEqual(28, self.benchmark_definition1.revision)
        self.assertEqual(28, execution.revision_target)
        self.assertEqual('BenchmarkDefinition1', execution.definition.name)
        self.assertEqual('0000200002000020000200002000020000200002', execution.commit.commit_hash)
        self.assertEqual('worker-name-1', execution.worker.name)

    def test_third_execution_available_does_not_exist_after_all_taken(self):
        execution = BenchmarkExecutionController.get_earliest_available_execution(self.user1)
        self.assertNotEqual(None, execution)

        execution = BenchmarkExecutionController.get_earliest_available_execution(self.user1)
        self.assertNotEqual(None, execution)

        execution = BenchmarkExecutionController.get_earliest_available_execution(self.user1)
        self.assertEqual(None, execution)

    def test_earliest_available_execution_of_user_2_is_execution_3(self):
        execution = BenchmarkExecutionController.get_earliest_available_execution(self.user2)

        self.assertNotEqual(None, execution)
        self.assertEqual(self.benchmark_execution3, execution)
        self.assertEqual(BenchmarkExecutionEntry.IN_PROGRESS, execution.status)
        self.assertEqual(False, execution.invalidated)
        self.assertEqual(3, self.benchmark_definition2.revision)
        self.assertEqual(3, execution.revision_target)
        self.assertEqual('BenchmarkDefinition2', execution.definition.name)
        self.assertEqual('0000100001000010000100001000010000100001', execution.commit.commit_hash)
        self.assertEqual('worker-name-2', execution.worker.name)
            

    def test_earliest_available_is_an_invalidated_one(self):
        self.benchmark_execution1.invalidated = True
        self.benchmark_execution1.save()
        self.benchmark_execution1.status = BenchmarkExecutionEntry.FINISHED
        self.benchmark_execution2.status = BenchmarkExecutionEntry.FINISHED
        self.benchmark_execution2.save()

        execution = BenchmarkExecutionController.get_earliest_available_execution(self.user1)

        self.assertNotEqual(None, execution)
        self.assertEqual(self.benchmark_execution1, execution)
        self.assertEqual(BenchmarkExecutionEntry.IN_PROGRESS, execution.status)
        self.assertEqual(False, execution.invalidated)
        self.assertEqual(28, self.benchmark_definition1.revision)
        self.assertEqual(28, execution.revision_target)
        self.assertEqual('BenchmarkDefinition1', execution.definition.name)
        self.assertEqual('0000100001000010000100001000010000100001', execution.commit.commit_hash)
        self.assertEqual('worker-name-1', execution.worker.name)

    def test_user_anonymous_allways_get_none_benchmark_execution(self):
        anonymous = AnonymousUser()
        execution1 = BenchmarkExecutionController.get_earliest_available_execution(anonymous)
        execution2 = BenchmarkExecutionController.get_earliest_available_execution(anonymous)
        execution3 = BenchmarkExecutionController.get_earliest_available_execution(anonymous)

        self.assertEqual(None, execution1)
        self.assertEqual(None, execution2)
        self.assertEqual(None, execution3)

    def test_create_bench_executions_from_commit_definition_and_worker(self):
        exec_entries = BenchmarkExecutionEntry.objects.all()
        for exec_entry in exec_entries:
            exec_entries.delete()

        self.assertEqual(0, BenchmarkExecutionEntry.objects.all().count())

        BenchmarkExecutionController.create_bench_executions_from_commit(
            self.commit1,
            [self.benchmark_definition1],
            [self.worker1]
        )

        self.assertEqual(1, BenchmarkExecutionEntry.objects.all().count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(
            commit=self.commit1,
            worker=self.worker1,
            definition=self.benchmark_definition1).count())

    def test_create_bench_executions_from_commit_definitions_and_workers(self):
        exec_entries = BenchmarkExecutionEntry.objects.all()
        for exec_entry in exec_entries:
            exec_entries.delete()

        self.assertEqual(0, BenchmarkExecutionEntry.objects.all().count())

        BenchmarkExecutionController.create_bench_executions_from_commit(
            self.commit1,
            [self.benchmark_definition1, self.benchmark_definition2],
            [self.worker1, self.worker2]
        )

        self.assertEqual(4, BenchmarkExecutionEntry.objects.all().count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(
            commit=self.commit1,
            worker=self.worker1,
            definition=self.benchmark_definition1).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(
            commit=self.commit1,
            worker=self.worker2,
            definition=self.benchmark_definition1).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(
            commit=self.commit1,
            worker=self.worker1,
            definition=self.benchmark_definition2).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(
            commit=self.commit1,
            worker=self.worker2,
            definition=self.benchmark_definition2).count())

    def test_create_bench_executions_froms_commits(self):
        BenchmarkExecutionEntry.objects.all().delete()

        commit_hashes = []
        commit_hashes.append('0000100001000010000100001000010000100001')
        commit_hashes.append('0000200002000020000200002000020000200002')
        commit_hashes.append('0000300003000030000300003000030000300003')

        self.assertEqual(0, BenchmarkExecutionEntry.objects.all().count())

        BenchmarkExecutionController.create_bench_executions_from_commits(self.git_project1, commit_hashes)

        self.assertEqual(12, BenchmarkExecutionEntry.objects.all().count())

        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(definition=self.benchmark_definition1, commit=self.commit1, worker=self.worker1).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(definition=self.benchmark_definition1, commit=self.commit1, worker=self.worker2).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(definition=self.benchmark_definition1, commit=self.commit2, worker=self.worker1).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(definition=self.benchmark_definition1, commit=self.commit2, worker=self.worker2).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(definition=self.benchmark_definition1, commit=self.commit3, worker=self.worker1).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(definition=self.benchmark_definition1, commit=self.commit3, worker=self.worker2).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(definition=self.benchmark_definition2, commit=self.commit1, worker=self.worker1).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(definition=self.benchmark_definition2, commit=self.commit1, worker=self.worker2).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(definition=self.benchmark_definition2, commit=self.commit2, worker=self.worker1).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(definition=self.benchmark_definition2, commit=self.commit2, worker=self.worker2).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(definition=self.benchmark_definition2, commit=self.commit3, worker=self.worker1).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(definition=self.benchmark_definition2, commit=self.commit3, worker=self.worker2).count())


    def test_create_bench_executions_from_worker_definitions_and_commits(self):
        exec_entries = BenchmarkExecutionEntry.objects.all()
        for exec_entry in exec_entries:
            exec_entries.delete()

        self.assertEqual(0, BenchmarkExecutionEntry.objects.all().count())

        BenchmarkExecutionController.create_bench_executions_from_worker(
            self.worker1,
            [self.commit1, self.commit2, self.commit3],
            [self.benchmark_definition1, self.benchmark_definition2]
        )

        self.assertEqual(6, BenchmarkExecutionEntry.objects.all().count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(
            commit=self.commit1,
            worker=self.worker1,
            definition=self.benchmark_definition1).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(
            commit=self.commit2,
            worker=self.worker1,
            definition=self.benchmark_definition1).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(
            commit=self.commit3,
            worker=self.worker1,
            definition=self.benchmark_definition1).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(
            commit=self.commit1,
            worker=self.worker1,
            definition=self.benchmark_definition2).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(
            commit=self.commit2,
            worker=self.worker1,
            definition=self.benchmark_definition2).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(
            commit=self.commit3,
            worker=self.worker1,
            definition=self.benchmark_definition2).count())

    def test_create_bench_executions_from_definition_commits_and_workers(self):
        exec_entries = BenchmarkExecutionEntry.objects.all()
        for exec_entry in exec_entries:
            exec_entries.delete()

        self.assertEqual(0, BenchmarkExecutionEntry.objects.all().count())

        BenchmarkExecutionController.create_bench_executions_from_definition(
            self.benchmark_definition1,
            [self.commit1, self.commit2, self.commit3],
            [self.worker1, self.worker2]
        )

        self.assertEqual(6, BenchmarkExecutionEntry.objects.all().count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(
            commit=self.commit1,
            worker=self.worker1,
            definition=self.benchmark_definition1).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(
            commit=self.commit2,
            worker=self.worker1,
            definition=self.benchmark_definition1).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(
            commit=self.commit3,
            worker=self.worker1,
            definition=self.benchmark_definition1).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(
            commit=self.commit1,
            worker=self.worker2,
            definition=self.benchmark_definition1).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(
            commit=self.commit2,
            worker=self.worker2,
            definition=self.benchmark_definition1).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(
            commit=self.commit3,
            worker=self.worker2,
            definition=self.benchmark_definition1).count())

    def test_create_bench_executions_only_creates_one_unique_execution(self):
        exec_entries = BenchmarkExecutionEntry.objects.all()
        for exec_entry in exec_entries:
            exec_entries.delete()

        self.assertEqual(0, BenchmarkExecutionEntry.objects.all().count())

        BenchmarkExecutionController.create_benchmark_execution(self.benchmark_definition1, self.commit1, self.worker1)
        BenchmarkExecutionController.create_benchmark_execution(self.benchmark_definition1, self.commit1, self.worker1)
        BenchmarkExecutionController.create_benchmark_execution(self.benchmark_definition1, self.commit1, self.worker1)
        BenchmarkExecutionController.create_benchmark_execution(self.benchmark_definition1, self.commit1, self.worker1)
        BenchmarkExecutionController.create_benchmark_execution(self.benchmark_definition1, self.commit1, self.worker1)
        BenchmarkExecutionController.create_benchmark_execution(self.benchmark_definition1, self.commit1, self.worker1)

        self.assertEqual(1, BenchmarkExecutionEntry.objects.all().count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(
            commit=self.commit1,
            worker=self.worker1,
            definition=self.benchmark_definition1).count())

    def test_create_bench_executions_and_those_are_unique(self):
        exec_entries = BenchmarkExecutionEntry.objects.all()
        for exec_entry in exec_entries:
            exec_entries.delete()

        self.assertEqual(0, BenchmarkExecutionEntry.objects.all().count())

        BenchmarkExecutionController.create_bench_executions_from_definition(
            self.benchmark_definition1,
            [self.commit1, self.commit2, self.commit3],
            [self.worker1, self.worker2]
        )

        BenchmarkExecutionController.create_bench_executions_from_definition(
            self.benchmark_definition1,
            [self.commit1, self.commit2, self.commit3],
            [self.worker1, self.worker2]
        )

        BenchmarkExecutionController.create_bench_executions_from_definition(
            self.benchmark_definition1,
            [self.commit1, self.commit2, self.commit3],
            [self.worker1, self.worker2]
        )

        self.assertEqual(6, BenchmarkExecutionEntry.objects.all().count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(
            commit=self.commit1,
            worker=self.worker1,
            definition=self.benchmark_definition1).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(
            commit=self.commit2,
            worker=self.worker1,
            definition=self.benchmark_definition1).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(
            commit=self.commit3,
            worker=self.worker1,
            definition=self.benchmark_definition1).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(
            commit=self.commit1,
            worker=self.worker2,
            definition=self.benchmark_definition1).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(
            commit=self.commit2,
            worker=self.worker2,
            definition=self.benchmark_definition1).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(
            commit=self.commit3,
            worker=self.worker2,
            definition=self.benchmark_definition1).count())


    def test_delete_benchmark_executions_from_definition(self):
        BenchmarkExecutionEntry.objects.all().delete()
        CommandGroupEntry.objects.all().delete()
        CommandSetEntry.objects.all().delete()

        self.assertEqual(0, BenchmarkExecutionEntry.objects.all().count())
        self.assertEqual(0, CommandGroupEntry.objects.all().count())
        self.assertEqual(0, CommandSetEntry.objects.all().count())

        BenchmarkExecutionController.create_bench_executions_from_commit(
            self.commit1,
            [self.benchmark_definition1],
            [self.worker1]
        )

        self.assertEqual(1, BenchmarkExecutionEntry.objects.all().count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(
            commit=self.commit1,
            worker=self.worker1,
            definition=self.benchmark_definition1).count())
        self.assertEqual(0, CommandGroupEntry.objects.all().count())
        self.assertEqual(1, CommandSetEntry.objects.all().count())

        BenchmarkExecutionController.delete_benchmark_executions(self.benchmark_definition1)

        self.assertEqual(0, BenchmarkExecutionEntry.objects.all().count())
        self.assertEqual(0, BenchmarkExecutionEntry.objects.filter(
            commit=self.commit1,
            worker=self.worker1,
            definition=self.benchmark_definition1).count())
        self.assertEqual(0, CommandGroupEntry.objects.all().count())
        self.assertEqual(0, CommandSetEntry.objects.all().count())
        self.assertEqual(0, CommandEntry.objects.all().count())
        self.assertEqual(0, CommandResultEntry.objects.all().count())

    def test_save_benchmark_execution(self):
        CommandEntry.objects.create(
            command_set=self.report3,
            command='command-custom-1',
            order=0
        )

        CommandEntry.objects.create(
            command_set=self.report3,
            command='command-custom-2',
            order=1
        )

        CommandEntry.objects.create(
            command_set=self.report3,
            command='command-custom-3',
            order=2
        )

        self.assertEqual(3, CommandEntry.objects.filter(command_set=self.report3).count())
        self.assertEqual(0, CommandResultEntry.objects.filter(command__command_set=self.report3).count())
        self.assertEqual('command-custom-1', CommandEntry.objects.filter(command_set=self.report3, order=0).first().command)
        self.assertEqual('command-custom-2', CommandEntry.objects.filter(command_set=self.report3, order=1).first().command)
        self.assertEqual('command-custom-3', CommandEntry.objects.filter(command_set=self.report3, order=2).first().command)
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(definition=self.benchmark_definition2).count())
        self.assertEqual(BenchmarkExecutionEntry.READY, BenchmarkExecutionEntry.objects.filter(definition=self.benchmark_definition2).first().status)

        result1 = {}
        result1['out'] = 'out1'
        result1['error'] = 'error1'
        result1['status'] = 1
        result1['start_time'] = timezone.now()
        result1['finish_time'] = timezone.now()

        result2 = {}
        result2['out'] = 'out2'
        result2['error'] = 'error2'
        result2['status'] = 2
        result2['start_time'] = timezone.now()
        result2['finish_time'] = timezone.now()

        result3 = {}
        result3['out'] = 'out3'
        result3['error'] = 'error3'
        result3['status'] = 3
        result3['start_time'] = timezone.now()
        result3['finish_time'] = timezone.now()

        command1 = {}
        command1['command'] = 'command-new-1'
        command1['result'] = result1

        command2 = {}
        command2['command'] = 'command-new-2'
        command2['result'] = result2

        command3 = {}
        command3['command'] = 'command-new-3'
        command3['result'] = result3

        report = {}
        report['command_set'] = [command1, command2, command3]

        BenchmarkExecutionController.save_bench_execution(self.benchmark_execution3, report)

        com1 = CommandEntry.objects.filter(command_set=self.report3, order=0).first()
        com2 = CommandEntry.objects.filter(command_set=self.report3, order=1).first()
        com3 = CommandEntry.objects.filter(command_set=self.report3, order=2).first()

        self.assertEqual(3, CommandEntry.objects.filter(command_set=self.report3).count())
        self.assertEqual('command-new-1', CommandEntry.objects.filter(command_set=self.report3, order=0).first().command)
        self.assertEqual('command-new-2', CommandEntry.objects.filter(command_set=self.report3, order=1).first().command)
        self.assertEqual('command-new-3', CommandEntry.objects.filter(command_set=self.report3, order=2).first().command)
        self.assertEqual(3, CommandResultEntry.objects.filter(command__command_set=self.report3).count())
        self.assertEqual('"out1"', CommandResultEntry.objects.filter(command=com1).first().out)
        self.assertEqual('error1', CommandResultEntry.objects.filter(command=com1).first().error)
        self.assertEqual(1, CommandResultEntry.objects.filter(command=com1).first().status)
        self.assertEqual('"out2"', CommandResultEntry.objects.filter(command=com2).first().out)
        self.assertEqual('error2', CommandResultEntry.objects.filter(command=com2).first().error)
        self.assertEqual(2, CommandResultEntry.objects.filter(command=com2).first().status)
        self.assertEqual('"out3"', CommandResultEntry.objects.filter(command=com3).first().out)
        self.assertEqual('error3', CommandResultEntry.objects.filter(command=com3).first().error)
        self.assertEqual(3, CommandResultEntry.objects.filter(command=com3).first().status)
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(definition=self.benchmark_definition2).count())
        self.assertEqual(BenchmarkExecutionEntry.FINISHED, BenchmarkExecutionEntry.objects.filter(definition=self.benchmark_definition2).first().status)

    def test_add_completed_benchmarks_to_branches_obj(self):

        # self.benchmark_execution1 = BenchmarkExecutionEntry.objects.create(
        #     definition=self.benchmark_definition1,
        #     commit=self.commit1,
        #     worker=self.worker1,
        #     report=self.report1,
        #     invalidated=False,
        #     revision_target=28,
        #     status=BenchmarkExecutionEntry.READY,
        # )

        # self.benchmark_execution2 = BenchmarkExecutionEntry.objects.create(
        #     definition=self.benchmark_definition1,
        #     commit=self.commit2,
        #     worker=self.worker1,
        #     report=self.report2,
        #     invalidated=False,
        #     revision_target=28,
        #     status=BenchmarkExecutionEntry.READY,
        # )

        be1_3_1 = BenchmarkExecutionEntry.objects.create(
            definition=self.benchmark_definition1,
            commit=self.commit3,
            worker=self.worker1,
            report=self.report2,
            invalidated=False,
            revision_target=28,
            status=BenchmarkExecutionEntry.FINISHED,
        )

        be1_1_2 = BenchmarkExecutionEntry.objects.create(
            definition=self.benchmark_definition1,
            commit=self.commit1,
            worker=self.worker2,
            report=self.report2,
            invalidated=True,
            revision_target=28,
            status=BenchmarkExecutionEntry.FINISHED,
        )

        be1_2_2 = BenchmarkExecutionEntry.objects.create(
            definition=self.benchmark_definition1,
            commit=self.commit2,
            worker=self.worker2,
            report=self.report2,
            invalidated=False,
            revision_target=28,
            status=BenchmarkExecutionEntry.IN_PROGRESS,
        )

        be1_3_2 = BenchmarkExecutionEntry.objects.create(
            definition=self.benchmark_definition1,
            commit=self.commit3,
            worker=self.worker2,
            report=self.report2,
            invalidated=False,
            revision_target=28,
            status=BenchmarkExecutionEntry.READY,
        )

        # self.benchmark_execution3 = BenchmarkExecutionEntry.objects.create(
        #     definition=self.benchmark_definition2,
        #     commit=self.commit1,
        #     worker=self.worker2,
        #     report=self.report3,
        #     invalidated=False,
        #     revision_target=2,
        #     status=BenchmarkExecutionEntry.READY,
        # )

        be2_2_2 = BenchmarkExecutionEntry.objects.create(
            definition=self.benchmark_definition2,
            commit=self.commit2,
            worker=self.worker2,
            report=self.report3,
            invalidated=False,
            revision_target=3,
            status=BenchmarkExecutionEntry.FINISHED,
        )

        be2_3_2 = BenchmarkExecutionEntry.objects.create(
            definition=self.benchmark_definition2,
            commit=self.commit3,
            worker=self.worker2,
            report=self.report3,
            invalidated=False,
            revision_target=2,
            status=BenchmarkExecutionEntry.FINISHED,
        )


        branch = {}
        branch['name'] = 'branch-name'
        branch['id'] = 28
        branch['merge_target'] = {}
        branch['branch_info'] = ''
        branch['commits'] = [
            {'hash' : '0000100001000010000100001000010000100001'},
            {'hash' : '0000200002000020000200002000020000200002'},
            {'hash' : '0000300003000030000300003000030000300003'}
        ]

        branches = [branch]

        branches = BenchmarkExecutionController.add_bench_exec_completed_to_branches(branches)

        self.assertEqual(3, len(branches[0]['commits']))
        self.assertEqual('0000100001000010000100001000010000100001', branches[0]['commits'][0]['hash'])
        self.assertEqual(0, branches[0]['commits'][0]['benchmark_completed'])
        self.assertEqual(33, branches[0]['commits'][1]['benchmark_completed'])
        self.assertEqual(33, branches[0]['commits'][2]['benchmark_completed'])

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

        fluctuation = BenchmarkExecutionController.get_benchmark_fluctuation(self.git_project1, commit2.commit_hash, 2)
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

        fluctuation = BenchmarkExecutionController.get_benchmark_fluctuation(self.git_project1, commit2.commit_hash, 2)
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

    def test_does_benchmark_fluctuation_exist(self):
        self.benchmark_definition1.max_fluctuation_percent = 5
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

        self.assertFalse(BenchmarkExecutionController.does_benchmark_fluctuation_exist(benchmark_execution0, 1))
        self.assertFalse(BenchmarkExecutionController.does_benchmark_fluctuation_exist(benchmark_execution1, 1))
        self.assertFalse(BenchmarkExecutionController.does_benchmark_fluctuation_exist(benchmark_execution2, 1))
        self.assertFalse(BenchmarkExecutionController.does_benchmark_fluctuation_exist(benchmark_execution3, 1))
        self.assertTrue(BenchmarkExecutionController.does_benchmark_fluctuation_exist(benchmark_execution4, 1))
        self.assertTrue(BenchmarkExecutionController.does_benchmark_fluctuation_exist(benchmark_execution5, 1))


