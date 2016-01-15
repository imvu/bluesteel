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
from app.logic.gitrepo.models.GitUserModel import GitUserEntry
from app.logic.gitrepo.models.GitCommitModel import GitCommitEntry
from app.logic.commandrepo.models.CommandModel import CommandEntry
from app.logic.commandrepo.models.CommandResultModel import CommandResultEntry
from app.logic.commandrepo.models.CommandSetModel import CommandSetEntry
from app.logic.commandrepo.models.CommandGroupModel import CommandGroupEntry
from app.logic.commandrepo.helper import TestCommandHelper
from app.logic.bluesteelworker.models.WorkerModel import WorkerEntry
from django.utils import timezone

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
        exec_entries = BenchmarkExecutionEntry.objects.all()
        for exec_entry in exec_entries:
            exec_entries.delete()

        com_group_entries = CommandGroupEntry.objects.all()
        for group_entry in com_group_entries:
            group_entry.delete()

        com_set_entries = CommandSetEntry.objects.all()
        for set_entry in com_set_entries:
            set_entry.delete()

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
        self.assertEqual(1, CommandGroupEntry.objects.all().count())
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
