""" BenchmarkDefinition Controller tests """

from django.test import TestCase
from app.logic.benchmark.controllers.BenchmarkDefinitionController import BenchmarkDefinitionController
from app.logic.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.logic.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.logic.bluesteel.controllers.BluesteelProjectController import BluesteelProjectController
from app.logic.commandrepo.models.CommandModel import CommandEntry
from app.logic.commandrepo.models.CommandResultModel import CommandResultEntry
from app.logic.commandrepo.models.CommandSetModel import CommandSetEntry
from app.logic.commandrepo.models.CommandGroupModel import CommandGroupEntry
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

        commands = []
        commands.append('command-28')
        commands.append('command-29')
        commands.append('command-30')

        definition = BenchmarkDefinitionController.save_benchmark_definition(definition.id, new_layout.id, project.id, commands)

        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-28').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-29').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-30').count())
        self.assertEqual(1, definition.revision)

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

        commands = []
        commands.append('command-1')
        commands.append('command-2')
        commands.append('command-3')

        result = BenchmarkDefinitionController.save_benchmark_definition(definition.id, new_layout.id, project.id, commands)
        definition = BenchmarkDefinitionEntry.objects.all().first()

        self.assertEqual(None, result)
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-1').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-2').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-3').count())
        self.assertEqual(0, definition.revision)

    def test_is_benchmark_definition_equivalent_layout(self):
        layout = BluesteelLayoutEntry.objects.create(name='default-name')
        project = BluesteelProjectController.create_default_project(layout, 'project', 0)
        definition = BenchmarkDefinitionController.create_default_benchmark_definition()

        self.assertEqual(False, BenchmarkDefinitionController.is_benchmark_definition_equivalent(definition.id, 2028, project.id, []))

    def test_is_benchmark_definition_equivalent_project(self):
        layout = BluesteelLayoutEntry.objects.create(name='default-name')
        project = BluesteelProjectController.create_default_project(layout, 'project', 0)
        definition = BenchmarkDefinitionController.create_default_benchmark_definition()

        self.assertEqual(False, BenchmarkDefinitionController.is_benchmark_definition_equivalent(definition.id, layout.id, 2028, []))

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
