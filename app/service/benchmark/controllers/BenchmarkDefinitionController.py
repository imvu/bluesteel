""" Benchmark Definition Controller file """

from app.service.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.service.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.service.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.util.commandrepo.models.CommandModel import CommandEntry
from app.util.commandrepo.models.CommandSetModel import CommandSetEntry

class BenchmarkDefinitionController(object):
    """ BenchmarkDefinition controller with helper functions """

    @staticmethod
    def create_default_definition_commands():
        """ Creates some default commands """
        com_set = CommandSetEntry.objects.create(name='bencharm-definition', order=0)
        CommandEntry.objects.create(command_set=com_set, command='command-1', order=0)
        CommandEntry.objects.create(command_set=com_set, command='command-2', order=1)
        CommandEntry.objects.create(command_set=com_set, command='command-3', order=2)
        return com_set

    @staticmethod
    def create_default_benchmark_definition():
        """ Creates a default benchmark definition """
        layout_entry = BluesteelLayoutEntry.objects.all().first()

        if layout_entry == None:
            return None

        project_entry = BluesteelProjectEntry.objects.filter(layout=layout_entry).first()

        if project_entry == None:
            return None

        default_commands = BenchmarkDefinitionController.create_default_definition_commands()

        definition = BenchmarkDefinitionEntry.objects.create(
            name='default-name',
            layout=layout_entry,
            project=project_entry,
            command_set=default_commands,
            revision=0
            )

        return definition
