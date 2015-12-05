""" BenchmarkExecution Controller tests """

from django.test import TestCase
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
from django.utils import timezone

class BenchmarkExecutionControllerTestCase(TestCase):

    def setUp(self):
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

    def test_earliest_available_execution_returns_none_if_no_definitions(self):
        self.assertEqual(0, BenchmarkDefinitionEntry.objects.all().count())
        self.assertEqual(None, BenchmarkExecutionController.get_earliest_available_execution())

    def test_earliest_available_execution_with_definition_1_and_commit_3(self):
        benchmark_definition = BenchmarkDefinitionEntry.objects.create(
            name='BenchmarkDefinition',
            layout=self.bluesteel_layout,
            project=self.bluesteel_project,
            command_set=self.command_set,
        )

        execution = BenchmarkExecutionController.get_earliest_available_execution()

        self.assertEqual(benchmark_definition, execution.definition)
        self.assertEqual('0000300003000030000300003000030000300003', execution.commit.commit_hash)
        self.assertEqual(BenchmarkExecutionEntry.IN_PROGRESS, execution.status)

    def test_ran_twice_with_commit_3_first_and_commit_2_second(self):
        benchmark_definition = BenchmarkDefinitionEntry.objects.create(
            name='BenchmarkDefinition',
            layout=self.bluesteel_layout,
            project=self.bluesteel_project,
            command_set=self.command_set,
        )

        execution1 = BenchmarkExecutionController.get_earliest_available_execution()

        self.assertEqual(benchmark_definition, execution1.definition)
        self.assertEqual('0000300003000030000300003000030000300003', execution1.commit.commit_hash)
        self.assertEqual(BenchmarkExecutionEntry.IN_PROGRESS, execution1.status)

        execution2 = BenchmarkExecutionController.get_earliest_available_execution()

        self.assertEqual(benchmark_definition, execution2.definition)
        self.assertEqual('0000200002000020000200002000020000200002', execution2.commit.commit_hash)
        self.assertEqual(BenchmarkExecutionEntry.IN_PROGRESS, execution2.status)

    def test_earliest_available_with_preexisting_executions(self):
        benchmark_definition = BenchmarkDefinitionEntry.objects.create(
            name='BenchmarkDefinition',
            layout=self.bluesteel_layout,
            project=self.bluesteel_project,
            command_set=self.command_set,
        )

        report = CommandSetEntry.objects.create(group=None)

        execution_commit_2 = BenchmarkExecutionEntry.objects.create(
            definition=benchmark_definition,
            commit=self.commit2,
            report=report,
            invalidated=False,
            revision_target=benchmark_definition.revision,
            status=BenchmarkExecutionEntry.FINISHED
        )

        execution1 = BenchmarkExecutionController.get_earliest_available_execution()

        self.assertEqual(benchmark_definition, execution1.definition)
        self.assertEqual('0000300003000030000300003000030000300003', execution1.commit.commit_hash)
        self.assertEqual(BenchmarkExecutionEntry.IN_PROGRESS, execution1.status)

        execution2 = BenchmarkExecutionController.get_earliest_available_execution()

        self.assertEqual(benchmark_definition, execution2.definition)
        self.assertEqual('0000100001000010000100001000010000100001', execution2.commit.commit_hash)
        self.assertEqual(BenchmarkExecutionEntry.IN_PROGRESS, execution2.status)

    def test_earliest_available_with_many_definitions_and_preexisting_executions(self):
        benchmark_definition1 = BenchmarkDefinitionEntry.objects.create(
            name='BenchmarkDefinition1',
            layout=self.bluesteel_layout,
            project=self.bluesteel_project,
            command_set=self.command_set,
        )

        benchmark_definition2 = BenchmarkDefinitionEntry.objects.create(
            name='BenchmarkDefinition2',
            layout=self.bluesteel_layout,
            project=self.bluesteel_project,
            command_set=self.command_set,
        )

        report = CommandSetEntry.objects.create(group=None)

        execution_commit_3_def_1 = BenchmarkExecutionEntry.objects.create(
            definition=benchmark_definition1,
            commit=self.commit3,
            report=report,
            invalidated=False,
            revision_target=benchmark_definition1.revision,
            status=BenchmarkExecutionEntry.FINISHED
        )

        execution_commit_3_def_2 = BenchmarkExecutionEntry.objects.create(
            definition=benchmark_definition2,
            commit=self.commit3,
            report=report,
            invalidated=False,
            revision_target=benchmark_definition2.revision,
            status=BenchmarkExecutionEntry.FINISHED
        )

        execution_commit_2_def_1 = BenchmarkExecutionEntry.objects.create(
            definition=benchmark_definition1,
            commit=self.commit2,
            report=report,
            invalidated=False,
            revision_target=benchmark_definition1.revision,
            status=BenchmarkExecutionEntry.FINISHED
        )

        execution1 = BenchmarkExecutionController.get_earliest_available_execution()

        self.assertEqual(benchmark_definition2, execution1.definition)
        self.assertEqual('0000200002000020000200002000020000200002', execution1.commit.commit_hash)
        self.assertEqual(BenchmarkExecutionEntry.IN_PROGRESS, execution1.status)

        execution2 = BenchmarkExecutionController.get_earliest_available_execution()

        self.assertEqual(benchmark_definition1, execution2.definition)
        self.assertEqual('0000100001000010000100001000010000100001', execution2.commit.commit_hash)
        self.assertEqual(BenchmarkExecutionEntry.IN_PROGRESS, execution2.status)

        execution3 = BenchmarkExecutionController.get_earliest_available_execution()

        self.assertEqual(benchmark_definition2, execution3.definition)
        self.assertEqual('0000100001000010000100001000010000100001', execution3.commit.commit_hash)
        self.assertEqual(BenchmarkExecutionEntry.IN_PROGRESS, execution3.status)

        execution4 = BenchmarkExecutionController.get_earliest_available_execution()

        self.assertEqual(None, execution4)


    def test_earliest_available_invalidated(self):
        benchmark_definition = BenchmarkDefinitionEntry.objects.create(
            name='BenchmarkDefinition',
            layout=self.bluesteel_layout,
            project=self.bluesteel_project,
            command_set=self.command_set,
        )

        report = CommandSetEntry.objects.create(group=None)

        execution_commit_3 = BenchmarkExecutionEntry.objects.create(
            definition=benchmark_definition,
            commit=self.commit3,
            report=report,
            invalidated=True,
            revision_target=benchmark_definition.revision,
            status=BenchmarkExecutionEntry.FINISHED
        )

        execution1 = BenchmarkExecutionController.get_earliest_available_execution()

        self.assertEqual(benchmark_definition, execution1.definition)
        self.assertEqual('0000300003000030000300003000030000300003', execution1.commit.commit_hash)
        self.assertEqual(BenchmarkExecutionEntry.IN_PROGRESS, execution1.status)
        self.assertEqual(False, execution1.invalidated)

        execution2 = BenchmarkExecutionController.get_earliest_available_execution()

        self.assertEqual(benchmark_definition, execution2.definition)
        self.assertEqual('0000200002000020000200002000020000200002', execution2.commit.commit_hash)
        self.assertEqual(BenchmarkExecutionEntry.IN_PROGRESS, execution2.status)

    def test_earliest_available_ready(self):
        benchmark_definition = BenchmarkDefinitionEntry.objects.create(
            name='BenchmarkDefinition',
            layout=self.bluesteel_layout,
            project=self.bluesteel_project,
            command_set=self.command_set,
        )

        report = CommandSetEntry.objects.create(group=None)

        execution_commit_3 = BenchmarkExecutionEntry.objects.create(
            definition=benchmark_definition,
            commit=self.commit3,
            report=report,
            invalidated=False,
            revision_target=benchmark_definition.revision,
            status=BenchmarkExecutionEntry.FINISHED
        )

        execution_commit_2 = BenchmarkExecutionEntry.objects.create(
            definition=benchmark_definition,
            commit=self.commit2,
            report=report,
            invalidated=False,
            revision_target=benchmark_definition.revision,
            status=BenchmarkExecutionEntry.READY
        )

        execution1 = BenchmarkExecutionController.get_earliest_available_execution()

        self.assertEqual(benchmark_definition, execution1.definition)
        self.assertEqual('0000200002000020000200002000020000200002', execution1.commit.commit_hash)
        self.assertEqual(BenchmarkExecutionEntry.IN_PROGRESS, execution1.status)
        self.assertEqual(False, execution1.invalidated)

        execution2 = BenchmarkExecutionController.get_earliest_available_execution()

        self.assertEqual(benchmark_definition, execution2.definition)
        self.assertEqual('0000100001000010000100001000010000100001', execution2.commit.commit_hash)
        self.assertEqual(BenchmarkExecutionEntry.IN_PROGRESS, execution2.status)


    def test_earliest_available_revision_mismatch(self):
        benchmark_definition = BenchmarkDefinitionEntry.objects.create(
            name='BenchmarkDefinition',
            layout=self.bluesteel_layout,
            project=self.bluesteel_project,
            command_set=self.command_set,
            revision=28,
        )

        report = CommandSetEntry.objects.create(group=None)

        execution_commit_2 = BenchmarkExecutionEntry.objects.create(
            definition=benchmark_definition,
            commit=self.commit2,
            report=report,
            invalidated=True,
            revision_target=0,
            status=BenchmarkExecutionEntry.FINISHED
        )

        execution1 = BenchmarkExecutionController.get_earliest_available_execution()

        self.assertEqual(benchmark_definition, execution1.definition)
        self.assertEqual('0000300003000030000300003000030000300003', execution1.commit.commit_hash)
        self.assertEqual(BenchmarkExecutionEntry.IN_PROGRESS, execution1.status)
        self.assertEqual(False, execution1.invalidated)
        self.assertEqual(28, execution1.revision_target)

        execution2 = BenchmarkExecutionController.get_earliest_available_execution()

        self.assertEqual(benchmark_definition, execution2.definition)
        self.assertEqual('0000200002000020000200002000020000200002', execution2.commit.commit_hash)
        self.assertEqual(BenchmarkExecutionEntry.IN_PROGRESS, execution2.status)
        self.assertEqual(False, execution2.invalidated)
        self.assertEqual(28, execution2.revision_target)
