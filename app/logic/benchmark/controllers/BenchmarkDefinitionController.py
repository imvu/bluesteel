""" Benchmark Definition Controller file """

# Disable warning for max 7 params on a function.
# I need to refactor save_benchmark_definition to take an object instead.
# pylint: disable=R0913

from django.core.paginator import Paginator
from app.logic.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.logic.benchmark.models.BenchmarkDefinitionWorkerPassModel import BenchmarkDefinitionWorkerPassEntry
from app.logic.benchmark.models.BenchmarkFluctuationOverrideModel import BenchmarkFluctuationOverrideEntry
from app.logic.benchmark.models.BenchmarkExecutionModel import BenchmarkExecutionEntry
from app.logic.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.logic.bluesteelworker.models.WorkerModel import WorkerEntry
from app.logic.commandrepo.controllers import CommandController
from app.logic.commandrepo.models.CommandModel import CommandEntry
from app.logic.commandrepo.models.CommandSetModel import CommandSetEntry
from app.logic.httpcommon.Page import Page
from app.logic.httpcommon import pag

class BenchmarkDefinitionController(object):
    """ BenchmarkDefinition controller with helper functions """

    @staticmethod
    def create_default_definition_commands():
        """ Creates some default commands """
        com_set = CommandSetEntry.objects.create(name='bencharm-definition', order=0)
        CommandEntry.objects.create(command_set=com_set, command='git checkout {commit_hash}', order=0)
        CommandEntry.objects.create(command_set=com_set, command='git submodule update --init --recursive', order=1)
        CommandEntry.objects.create(command_set=com_set, command='<add_more_commands_here>', order=2)
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
    def duplicate_benchmark_definition(bench_definition_id):
        """ Duplicates a Benchmark Definition except for the Overrides """
        bench_def = BenchmarkDefinitionEntry.objects.filter(id=bench_definition_id).first()

        if bench_def is None:
            return None

        new_comm_set = CommandController.CommandController.duplicate_command_set(bench_def.command_set.id)

        if new_comm_set is None:
            return None

        new_bench_def = BenchmarkDefinitionEntry.objects.create(
            name=bench_def.name + ' (duplicate)',
            layout=bench_def.layout,
            project=bench_def.project,
            command_set=new_comm_set,
            active=False,
            revision=0,
            max_fluctuation_percent=bench_def.max_fluctuation_percent,
            max_weeks_old_notify=bench_def.max_weeks_old_notify,
        )

        return new_bench_def


    @staticmethod
    def populate_worker_passes_for_definition(bench_def):
        """ Creates all the missing worker passes for a benchmark definition """
        all_workers = WorkerEntry.objects.all()

        for worker in all_workers:
            BenchmarkDefinitionWorkerPassEntry.objects.get_or_create(
                definition=bench_def,
                worker=worker)


    @staticmethod
    def populate_worker_passes_all_definitions():
        definitions = BenchmarkDefinitionEntry.objects.all()
        for definition in definitions:
            BenchmarkDefinitionController.populate_worker_passes_for_definition(definition)


    @staticmethod
    def save_benchmark_definition(
            name,
            benchmark_definition_id,
            layout_id,
            project_id,
            active,
            command_list,
            max_fluctuation_percent,
            overrides,
            max_weeks_old_notify,
            work_passes):
        """ Save benchmark definition with the new data provided, returns None if error """
        benchmark_def_entry = BenchmarkDefinitionEntry.objects.filter(id=benchmark_definition_id).first()

        if benchmark_def_entry is None:
            return None

        BenchmarkFluctuationOverrideEntry.objects.filter(definition__id=benchmark_definition_id).delete()

        for override in overrides:
            BenchmarkFluctuationOverrideEntry.objects.create(
                definition=benchmark_def_entry,
                result_id=override['result_id'],
                override_value=override['override_value'],
            )

        BenchmarkDefinitionController.save_work_passes(work_passes, benchmark_definition_id)

        if BenchmarkDefinitionController.is_benchmark_definition_equivalent(
                benchmark_definition_id,
                layout_id,
                project_id,
                command_list):
            benchmark_def_entry.name = name
            benchmark_def_entry.max_fluctuation_percent = max_fluctuation_percent
            benchmark_def_entry.max_weeks_old_notify = max_weeks_old_notify
            benchmark_def_entry.active = active
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
            benchmark_def_entry.active = active
            benchmark_def_entry.save()
            return None

        CommandController.CommandController.delete_commands_of_command_set(benchmark_def_entry.command_set)
        CommandController.CommandController.add_commands_to_command_set(benchmark_def_entry.command_set, command_list)

        if (benchmark_def_entry.layout.id != layout_id) or (benchmark_def_entry.project.id != project_id):
            BenchmarkExecutionEntry.objects.filter(definition__id=benchmark_definition_id).delete()

        benchmark_def_entry.name = name
        benchmark_def_entry.layout = layout_entry
        benchmark_def_entry.project = project_entry
        benchmark_def_entry.active = active
        benchmark_def_entry.revision = benchmark_def_entry.revision + 1
        benchmark_def_entry.max_fluctuation_percent = max_fluctuation_percent
        benchmark_def_entry.max_weeks_old_notify = max_weeks_old_notify
        benchmark_def_entry.save()

        return benchmark_def_entry

    @staticmethod
    def save_work_passes(work_passes, benchmark_definition_id):
        """ Contains the logic to read work passes info and save it into the models """
        for work_pass in work_passes:
            definition = BenchmarkDefinitionEntry.objects.filter(id=benchmark_definition_id).first()
            if not definition:
                continue


            worker = WorkerEntry.objects.filter(id=work_pass['id']).first()
            if not worker:
                continue

            (entry, created) = BenchmarkDefinitionWorkerPassEntry.objects.get_or_create(
                definition=definition,
                worker=worker)
            del created
            entry.allowed = work_pass['allowed']
            entry.save()


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

        return False

    @staticmethod
    def get_benchmark_definition(benchmark_definition_id):
        """ Returns Benchmark Definitions given a page index """
        def_entry = BenchmarkDefinitionEntry.objects.filter(id=benchmark_definition_id).first()

        if def_entry is None:
            return None

        def_obj = def_entry.as_object()
        def_obj['fluctuation_overrides'] = []
        def_obj['work_passes'] = []

        flucs = BenchmarkFluctuationOverrideEntry.objects.filter(definition__id=benchmark_definition_id)
        for fluc in flucs:
            obj = {}
            obj['result_id'] = fluc.result_id
            obj['override_value'] = fluc.override_value
            def_obj['fluctuation_overrides'].append(obj)

        work_passes = BenchmarkDefinitionWorkerPassEntry.objects.filter(definition__id=def_entry.id)
        for work_pass in work_passes:
            def_obj['work_passes'].append(work_pass.as_object())

        return def_obj



    @staticmethod
    def get_benchmark_definitions_with_pagination(items_per_page, page_index, pagination_half_range):
        """ Returns Benchmark Definitions given a page index """
        def_entries = BenchmarkDefinitionEntry.objects.all().order_by('-active', 'name')

        page = Page(items_per_page, page_index)
        pager = Paginator(def_entries, page.items_per_page)
        current_page = pager.page(page.page_index)
        def_entries = current_page.object_list
        page_indices = pag.get_pagination_indices(page, pagination_half_range, pager.num_pages)

        definitions = []

        for def_entry in def_entries:
            def_obj = def_entry.as_object()
            def_obj['fluctuation_overrides'] = []
            def_obj['work_passes'] = []

            flucs = BenchmarkFluctuationOverrideEntry.objects.filter(definition__id=def_entry.id)
            for fluc in flucs:
                obj = {}
                obj['result_id'] = fluc.result_id
                obj['override_value'] = fluc.override_value
                def_obj['fluctuation_overrides'].append(obj)

            work_passes = BenchmarkDefinitionWorkerPassEntry.objects.filter(definition__id=def_entry.id)
            for work_pass in work_passes:
                def_obj['work_passes'].append(work_pass.as_object())

            definitions.append(def_obj)

        return (definitions, page_indices)
