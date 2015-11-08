""" BenchmarkDefinition Controller tests """

from django.test import TestCase
from app.service.benchmark.controllers.BenchmarkDefinitionController import BenchmarkDefinitionController
from app.service.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.service.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.service.bluesteel.controllers.BluesteelProjectController import BluesteelProjectController
from app.util.commandrepo.models.CommandModel import CommandEntry
from app.util.commandrepo.models.CommandResultModel import CommandResultEntry
from app.util.commandrepo.models.CommandSetModel import CommandSetEntry
from app.util.commandrepo.models.CommandGroupModel import CommandGroupEntry
from app.util.commandrepo.helper import TestCommandHelper

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

        commands = []
        commands.append('command-28')
        commands.append('command-29')
        commands.append('command-30')

        definition = BenchmarkDefinitionController.save_benchmark_definition(definition.id, new_layout.id, project.id, commands)

        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-28').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-29').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-30').count())
