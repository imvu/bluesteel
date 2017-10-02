""" Presenter json views, benchmark definition page functions """

# Duplicate code
# pylint: disable=R0801

from django.db import transaction
from app.presenter.views.helpers import ViewUrlGenerator
from app.presenter.schemas import BenchmarkDefinitionSchemas
from app.logic.benchmark.controllers.BenchmarkDefinitionController import BenchmarkDefinitionController
from app.logic.benchmark.models.BenchmarkDefinitionWorkerPassModel import BenchmarkDefinitionWorkerPassEntry
from app.logic.httpcommon import res, val

@transaction.atomic
def create_new_benchmark_definition(request):
    """ Creates a new benchmark defintion """
    if request.method != 'POST':
        return res.get_response(400, 'Only post allowed', {})

    definition = BenchmarkDefinitionController.create_default_benchmark_definition()
    BenchmarkDefinitionController.populate_worker_passes_for_definition(definition)

    data = {}
    data['redirect'] = ViewUrlGenerator.get_benchmark_definitions_url(1)

    return res.get_response(200, 'Benchmark definition created', data)

@transaction.atomic
def view_duplicate_benchmark_definition(request, benchmark_definition_id):
    """ Duplicate benchmark definition properties """
    if request.method != 'POST':
        return res.get_only_post_allowed({})

    dup_bench_entry = BenchmarkDefinitionController.duplicate_benchmark_definition(benchmark_definition_id)

    if dup_bench_entry is None:
        return res.get_response(404, 'Benchmark Defintion save error', {})

    data = {}
    data['redirect'] = ViewUrlGenerator.get_benchmark_definition_url(dup_bench_entry.id)

    return res.get_response(200, 'Benchmark Definition saved', data)


@transaction.atomic
def view_save_benchmark_definition(request, benchmark_definition_id):
    """ Save benchmark definition properties """
    if request.method != 'POST':
        return res.get_only_post_allowed({})

    (json_valid_value, post_info) = val.validate_json_string(request.body)
    if not json_valid_value:
        return res.get_json_parser_failed({})

    (obj_validated, val_resp_obj) = val.validate_obj_schema(
        post_info,
        BenchmarkDefinitionSchemas.SAVE_BENCHMARK_DEFINITION
    )

    if not obj_validated:
        return res.get_schema_failed(val_resp_obj)

    bench_entry = BenchmarkDefinitionController.save_benchmark_definition(
        benchmark_definition_id=benchmark_definition_id,
        name=val_resp_obj['name'],
        layout_id=val_resp_obj['layout_id'],
        project_id=val_resp_obj['project_id'],
        priority=val_resp_obj['priority'],
        active=val_resp_obj['active'],
        command_list=val_resp_obj['command_list'],
        max_fluctuation_percent=val_resp_obj['max_fluctuation_percent'],
        overrides=val_resp_obj['overrides'],
        max_weeks_old_notify=val_resp_obj['max_weeks_old_notify'],
        work_passes=val_resp_obj['work_passes'],
    )

    if bench_entry is None:
        return res.get_response(404, 'Benchmark Defintion save error', {})

    return res.get_response(200, 'Benchmark Definition saved', {})


@transaction.atomic
def view_delete_benchmark_definition(request, benchmark_definition_id):
    """ Delete benchmark definition properties """
    if request.method != 'POST':
        return res.get_only_post_allowed({})

    ret = BenchmarkDefinitionController.delete_benchmark_definition(
        benchmark_definition_id=benchmark_definition_id
    )

    data = {}
    data['redirect'] = ViewUrlGenerator.get_benchmark_definitions_url(1)
    data['benchmark_definition_id'] = benchmark_definition_id

    if ret:
        return res.get_response(200, 'Benchmark Defintion deleted', data)

    return res.get_response(404, 'Benchmark Definition not found', data)



def get_worker_names_and_ids_of_definition(request, benchmark_definition_id):
    """ Returns the list of all workers plus ids associated with a benchmark definition """
    if request.method != 'GET':
        return res.get_only_get_allowed({})

    bench_passes = BenchmarkDefinitionWorkerPassEntry.objects.filter(
        definition__id=benchmark_definition_id,
        allowed=True)

    data = {}
    data['workers'] = []

    for bench_pass in bench_passes:
        obj = {}
        obj['name'] = bench_pass.worker.name
        obj['id'] = bench_pass.worker.id
        obj['operative_system'] = bench_pass.worker.operative_system
        data['workers'].append(obj)

    return res.get_response(200, 'Worker list', data)
