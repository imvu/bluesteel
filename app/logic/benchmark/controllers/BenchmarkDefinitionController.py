""" Benchmark Definition Controller file """

from app.logic.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.logic.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.logic.commandrepo.controllers import CommandController
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

        if layout_entry is None:
            return None

        project_entry = BluesteelProjectEntry.objects.filter(layout=layout_entry).first()

        if project_entry is None:
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
    def save_benchmark_definition(
            name,
            benchmark_definition_id,
            layout_id,
            project_id,
            command_list,
            max_fluctuation_percent,
            max_weeks_old_notify):
        """ Save benchmark definition with the new data provided, returns None if error """
        benchmark_def_entry = BenchmarkDefinitionEntry.objects.filter(id=benchmark_definition_id).first()

        if benchmark_def_entry is None:
            return None

        if BenchmarkDefinitionController.is_benchmark_definition_equivalent(
                benchmark_definition_id,
                layout_id,
                project_id,
                command_list):
            benchmark_def_entry.name = name
            benchmark_def_entry.max_fluctuation_percent = max_fluctuation_percent
            benchmark_def_entry.max_weeks_old_notify = max_weeks_old_notify
            benchmark_def_entry.save()
            return benchmark_def_entry

        layout_entry = BluesteelLayoutEntry.objects.filter(id=layout_id).first()

        if layout_entry is None:
            return None

        project_entry = BluesteelProjectEntry.objects.filter(layout=layout_entry, id=project_id).first()

        if project_entry is None:
            project_entry = BluesteelProjectEntry.objects.filter(layout=layout_entry).first()
            benchmark_def_entry.name = name
            benchmark_def_entry.layout = layout_entry
            benchmark_def_entry.project = project_entry
            benchmark_def_entry.save()
            return None

        CommandController.CommandController.delete_commands_of_command_set(benchmark_def_entry.command_set)
        CommandController.CommandController.add_commands_to_command_set(benchmark_def_entry.command_set, command_list)

        benchmark_def_entry.name = name
        benchmark_def_entry.layout = layout_entry
        benchmark_def_entry.project = project_entry
        benchmark_def_entry.revision = benchmark_def_entry.revision + 1
        benchmark_def_entry.max_fluctuation_percent = max_fluctuation_percent
        benchmark_def_entry.max_weeks_old_notify = max_weeks_old_notify
        benchmark_def_entry.save()

        return benchmark_def_entry

    @staticmethod
    def is_benchmark_definition_equivalent(benchmark_definition_id, layout_id, project_id, command_list):
        """ Returns true if the new information to be saved is equivalent to the stored one """
        benchmark_def_entry = BenchmarkDefinitionEntry.objects.filter(id=benchmark_definition_id).first()

        if benchmark_def_entry is None:
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

    @staticmethod
    def delete_benchmark_definition(benchmark_definition_id):
        """ Deletes benchmark defintion from its id """

        bench_def_entry = BenchmarkDefinitionEntry.objects.filter(id=benchmark_definition_id).first()

        if bench_def_entry:
            bench_def_entry.delete()
            return True
        else:
            return False
