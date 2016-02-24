""" BenchmarkDefinition Controller tests """

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from app.logic.benchmark.controllers.BenchmarkDefinitionController import BenchmarkDefinitionController
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
from app.logic.bluesteelworker.models.WorkerModel import WorkerEntry
from app.logic.commandrepo.helper import TestCommandHelper

class BenchmarkDefinitionControllerTestCase(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_default_definition_commands(self):
        self.assertEqual(0, CommandGroupEntry.objects.all().count())
        self.assertEqual(0, CommandSetEntry.objects.all().count())
        self.assertEqual(0, CommandEntry.objects.all().count())
        self.assertEqual(0, CommandResultEntry.objects.all().count())

        BenchmarkDefinitionController.create_default_definition_commands()

        self.assertEqual(0, CommandGroupEntry.objects.all().count())
        self.assertEqual(1, CommandSetEntry.objects.all().count())
        self.assertEqual(3, CommandEntry.objects.all().count())
        self.assertEqual(0, CommandResultEntry.objects.all().count())

    def test_create_default_benchmark_definition_without_layout_returns_nothing(self):
        self.assertEqual(0, BluesteelLayoutEntry.objects.all().count())
        self.assertEqual(0, BluesteelProjectEntry.objects.all().count())
        self.assertEqual(None, BenchmarkDefinitionController.create_default_benchmark_definition())

    def test_create_default_benchmark_definition_without_projects_returns_nothing(self):
        new_layout = BluesteelLayoutEntry.objects.create(name='default-name')

        self.assertEqual(1, BluesteelLayoutEntry.objects.all().count())
        self.assertEqual(0, BluesteelProjectEntry.objects.all().count())
        self.assertEqual(None, BenchmarkDefinitionController.create_default_benchmark_definition())


    def test_create_default_benchmark_definition_without_projects_returns_nothing(self):
        self.assertEqual(0, CommandGroupEntry.objects.all().count())
        self.assertEqual(0, CommandSetEntry.objects.all().count())
        self.assertEqual(0, CommandEntry.objects.all().count())
        self.assertEqual(0, CommandResultEntry.objects.all().count())

        new_layout = BluesteelLayoutEntry.objects.create(name='default-name')
        project = BluesteelProjectController.create_default_project(new_layout, 'project', 0)
        definition = BenchmarkDefinitionController.create_default_benchmark_definition()

        self.assertEqual(1, BluesteelLayoutEntry.objects.all().count())
        self.assertEqual(1, BluesteelProjectEntry.objects.all().count())
        self.assertNotEqual(None, definition.command_set)
        self.assertEqual(3, CommandEntry.objects.filter(command_set=definition.command_set).count())
        self.assertEqual(0, CommandResultEntry.objects.all().count())


    def test_save_benchmark_definition(self):
        self.assertEqual(0, CommandGroupEntry.objects.all().count())
        self.assertEqual(0, CommandSetEntry.objects.all().count())
        self.assertEqual(0, CommandEntry.objects.all().count())
        self.assertEqual(0, CommandResultEntry.objects.all().count())

        new_layout = BluesteelLayoutEntry.objects.create(name='default-name')
        project = BluesteelProjectController.create_default_project(new_layout, 'project', 0)
        definition = BenchmarkDefinitionController.create_default_benchmark_definition()

        self.assertEqual(1, BluesteelLayoutEntry.objects.all().count())
        self.assertEqual(1, BluesteelProjectEntry.objects.all().count())
        self.assertNotEqual(None, definition.command_set)
        self.assertEqual(3, CommandEntry.objects.filter(command_set=definition.command_set).count())
        self.assertEqual(0, CommandResultEntry.objects.all().count())
        self.assertEqual(0, definition.revision)
        self.assertEqual('default-name', definition.name)

        commands = []
        commands.append('command-28')
        commands.append('command-29')
        commands.append('command-30')

        definition = BenchmarkDefinitionController.save_benchmark_definition('new-name', definition.id, new_layout.id, project.id, commands)

        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-28').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-29').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-30').count())
        self.assertEqual(1, definition.revision)
        self.assertEqual('new-name', definition.name)

    def test_save_same_benchmark_definition_does_not_increment_revision(self):
        self.assertEqual(0, CommandGroupEntry.objects.all().count())
        self.assertEqual(0, CommandSetEntry.objects.all().count())
        self.assertEqual(0, CommandEntry.objects.all().count())
        self.assertEqual(0, CommandResultEntry.objects.all().count())

        new_layout = BluesteelLayoutEntry.objects.create(name='default-name')
        project = BluesteelProjectController.create_default_project(new_layout, 'project', 0)
        definition = BenchmarkDefinitionController.create_default_benchmark_definition()

        self.assertEqual(1, BluesteelLayoutEntry.objects.all().count())
        self.assertEqual(1, BluesteelProjectEntry.objects.all().count())
        self.assertNotEqual(None, definition.command_set)
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-1').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-2').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-3').count())
        self.assertEqual(0, CommandResultEntry.objects.all().count())
        self.assertEqual(0, definition.revision)
        self.assertEqual('default-name', definition.name)

        commands = []
        commands.append('command-1')
        commands.append('command-2')
        commands.append('command-3')

        result = BenchmarkDefinitionController.save_benchmark_definition('default-name', definition.id, new_layout.id, project.id, commands)
        definition = BenchmarkDefinitionEntry.objects.all().first()

        self.assertEqual(None, result)
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-1').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-2').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-3').count())
        self.assertEqual(0, definition.revision)
        self.assertEqual('default-name', definition.name)

    def test_save_benchmark_definition_does_not_delete_benchmarks_executions(self):
        user1 = User.objects.create_user('user1@test.com', 'user1@test.com', 'pass')
        user1.save()

        git_project1 = GitProjectEntry.objects.create(url='http://test/')

        git_user1 = GitUserEntry.objects.create(
            project=git_project1,
            name='user1',
            email='user1@test.com'
        )

        commit1 = GitCommitEntry.objects.create(
            project=git_project1,
            commit_hash='0000100001000010000100001000010000100001',
            author=git_user1,
            author_date=timezone.now(),
            committer=git_user1,
            committer_date=timezone.now()
        )

        command_group = CommandGroupEntry.objects.create()
        command_set = CommandSetEntry.objects.create(
            group=command_group
        )

        bluesteel_layout = BluesteelLayoutEntry.objects.create(
            name='Layout',
            active=True,
            project_index_path=0,
        )

        bluesteel_project = BluesteelProjectEntry.objects.create(
            name='Project',
            order=0,
            layout=bluesteel_layout,
            command_group=command_group,
            git_project=git_project1,
        )

        benchmark_definition1 = BenchmarkDefinitionEntry.objects.create(
            name='BenchmarkDefinition1',
            layout=bluesteel_layout,
            project=bluesteel_project,
            command_set=command_set,
            revision=28,
        )

        worker1 = WorkerEntry.objects.create(
            name='worker-name-1',
            uuid='uuid-worker-1',
            operative_system='osx',
            description='long-description-1',
            user=user1,
            git_feeder=False
        )

        report1 = CommandSetEntry.objects.create(group=None)

        benchmark_execution1 = BenchmarkExecutionEntry.objects.create(
            definition=benchmark_definition1,
            commit=commit1,
            worker=worker1,
            report=report1,
            invalidated=False,
            revision_target=28,
            status=BenchmarkExecutionEntry.READY,
        )

        commands = []
        commands.append('command-new-1')
        commands.append('command-new-2')
        commands.append('command-new-3')
        commands.append('command-new-4')
        commands.append('command-new-5')

        self.assertEqual('BenchmarkDefinition1', benchmark_definition1.name)
        self.assertEqual(1, BenchmarkExecutionEntry.objects.all().count())
        self.assertEqual(benchmark_execution1, BenchmarkExecutionEntry.objects.all().first())
        self.assertEqual(0, CommandEntry.objects.filter(command_set=benchmark_definition1.command_set).count())

        result = BenchmarkDefinitionController.save_benchmark_definition('BenchmarkDefinition1-1', benchmark_definition1.id, bluesteel_layout.id, bluesteel_project.id, commands)

        self.assertEqual('BenchmarkDefinition1-1', result.name)
        self.assertEqual(1, BenchmarkExecutionEntry.objects.all().count())
        self.assertEqual(benchmark_execution1, BenchmarkExecutionEntry.objects.all().first())
        self.assertEqual(5, CommandEntry.objects.filter(command_set=benchmark_definition1.command_set).count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=benchmark_definition1.command_set, command='command-new-1').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=benchmark_definition1.command_set, command='command-new-2').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=benchmark_definition1.command_set, command='command-new-3').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=benchmark_definition1.command_set, command='command-new-4').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=benchmark_definition1.command_set, command='command-new-5').count())

    def test_is_benchmark_definition_equivalent_layout(self):
        layout = BluesteelLayoutEntry.objects.create(name='default-name')
        project = BluesteelProjectController.create_default_project(layout, 'project', 0)
        definition = BenchmarkDefinitionController.create_default_benchmark_definition()

        commands = []
        commands.append('command-1')
        commands.append('command-2')
        commands.append('command-3')

        self.assertEqual(False, BenchmarkDefinitionController.is_benchmark_definition_equivalent(definition.id, 2028, project.id, commands))

    def test_is_benchmark_definition_equivalent_project(self):
        layout = BluesteelLayoutEntry.objects.create(name='default-name')
        project = BluesteelProjectController.create_default_project(layout, 'project', 0)
        definition = BenchmarkDefinitionController.create_default_benchmark_definition()

        commands = []
        commands.append('command-1')
        commands.append('command-2')
        commands.append('command-3')

        self.assertEqual(False, BenchmarkDefinitionController.is_benchmark_definition_equivalent(definition.id, layout.id, 2028, commands))

    def test_is_benchmark_definition_equivalent_commands(self):
        layout = BluesteelLayoutEntry.objects.create(name='default-name')
        project = BluesteelProjectController.create_default_project(layout, 'project', 0)
        definition = BenchmarkDefinitionController.create_default_benchmark_definition()

        commands = []
        commands.append('command-28')
        commands.append('command-29')
        commands.append('command-30')

        self.assertEqual(False, BenchmarkDefinitionController.is_benchmark_definition_equivalent(definition.id, layout.id, project.id, commands))

    def test_is_benchmark_definition_equivalent_all(self):
        layout = BluesteelLayoutEntry.objects.create(name='default-name')
        project = BluesteelProjectController.create_default_project(layout, 'project', 0)
        definition = BenchmarkDefinitionController.create_default_benchmark_definition()

        commands = []
        commands.append('command-1')
        commands.append('command-2')
        commands.append('command-3')

        self.assertEqual(True, BenchmarkDefinitionController.is_benchmark_definition_equivalent(definition.id, layout.id, project.id, commands))
