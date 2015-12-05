""" Benchmark Definition Controller file """

from app.logic.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.logic.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.logic.commandrepo.controllers.CommandController import CommandController
from app.logic.commandrepo.models.CommandModel import CommandEntry
from app.logic.commandrepo.models.CommandSetModel import CommandSetEntry

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

    @staticmethod
    def save_benchmark_definition(benchmark_definition_id, layout_id, project_id, command_list):
        """ Save benchmark definition with the new data provided, returns None if error """
        if BenchmarkDefinitionController.is_benchmark_definition_equivalent(
                benchmark_definition_id,
                layout_id,
                project_id,
                command_list):
            return None

        benchmark_def_entry = BenchmarkDefinitionEntry.objects.filter(id=benchmark_definition_id).first()

        if benchmark_def_entry == None:
            return None

        layout_entry = BluesteelLayoutEntry.objects.filter(id=layout_id).first()

        if layout_entry == None:
            return None

        project_entry = BluesteelProjectEntry.objects.filter(layout=layout_entry, id=project_id).first()

        if project_entry == None:
            project_entry = BluesteelProjectEntry.objects.filter(layout=layout_entry).first()
            benchmark_def_entry.layout = layout_entry
            benchmark_def_entry.project = project_entry
            benchmark_def_entry.save()
            return None

        CommandController.delete_command_set_by_id(benchmark_def_entry.command_set.id)
        new_com_set = CommandController.add_full_command_set(None, 'bench-com-set', 0, command_list)

        benchmark_def_entry.layout = layout_entry
        benchmark_def_entry.project = project_entry
        benchmark_def_entry.command_set = new_com_set
        benchmark_def_entry.revision = benchmark_def_entry.revision + 1
        benchmark_def_entry.save()

        return benchmark_def_entry

    @staticmethod
    def is_benchmark_definition_equivalent(benchmark_definition_id, layout_id, project_id, command_list):
        """ Returns true if the new information to be saved is equivalent to the stored one """
        benchmark_def_entry = BenchmarkDefinitionEntry.objects.filter(id=benchmark_definition_id).first()

        if benchmark_def_entry == None:
            return False

        if benchmark_def_entry.layout.id != layout_id:
            return False

        if benchmark_def_entry.project.id != project_id:
            return False

        com_entries = CommandEntry.objects.filter(command_set=benchmark_def_entry.command_set).order_by('order')

        if len(com_entries) != len(command_list):
            return False

        for index, com in enumerate(com_entries):
            if com.command != command_list[index]:
                return False

        return True
