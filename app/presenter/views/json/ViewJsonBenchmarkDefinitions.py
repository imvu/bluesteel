""" Presenter json views, benchmark definition page functions """

from django.db import transaction
from app.presenter.views.helpers import ViewUrlGenerator
from app.presenter.schemas import BenchmarkDefinitionSchemas
from app.logic.benchmark.controllers.BenchmarkDefinitionController import BenchmarkDefinitionController
from app.logic.benchmark.controllers.BenchmarkExecutionController import BenchmarkExecutionController
from app.logic.gitrepo.models.GitCommitModel import GitCommitEntry
from app.logic.bluesteelworker.models.WorkerModel import WorkerEntry
from app.logic.httpcommon import res, val

@transaction.atomic
def create_new_benchmark_definition(request):
    """ Creates a new benchmark defintion """
    if request.method == 'POST':

        bench_def = BenchmarkDefinitionController.create_default_benchmark_definition()

        commit_entries = GitCommitEntry.objects.filter(project=bench_def.project.git_project)
        worker_entries = WorkerEntry.objects.all()
        BenchmarkExecutionController.create_bench_executions_from_definition(
            bench_def_entry=bench_def,
            commit_entries=commit_entries,
            worker_entries=worker_entries
        )

        data = {}
        data['redirect'] = ViewUrlGenerator.get_benchmark_definitions_url(1)

        return res.get_response(200, 'Benchmark definition created', data)
    else:
        return res.get_response(400, 'Only post allowed', {})

@transaction.atomic
def view_save_benchmark_definition(request, benchmark_definition_id):
    """ Save benchmark definition properties """
    if request.method == 'POST':
        (json_valid, post_info) = val.validate_json_string(request.body)
        if not json_valid:
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
            command_list=val_resp_obj['command_list'],
            max_fluctuation_percent=val_resp_obj['max_fluctuation_percent'],
            overrides=val_resp_obj['overrides'],
            max_weeks_old_notify=val_resp_obj['max_weeks_old_notify']
        )

        if bench_entry is None:
            return res.get_response(404, 'Benchmark Defintion save error', {})
        else:
            return res.get_response(200, 'Benchmark Definition saved', {})
    else:
        return res.get_only_post_allowed({})

@transaction.atomic
def view_delete_benchmark_definition(request, benchmark_definition_id):
    """ Delete benchmark definition properties """
    if request.method == 'POST':
        ret = BenchmarkDefinitionController.delete_benchmark_definition(
            benchmark_definition_id=benchmark_definition_id
        )

        data = {}
        data['redirect'] = ViewUrlGenerator.get_benchmark_definitions_url(1)
        data['benchmark_definition_id'] = benchmark_definition_id

        if ret:
            return res.get_response(200, 'Benchmark Defintion deleted', data)
        else:
            return res.get_response(404, 'Benchmark Definition not found', data)
    else:
        return res.get_only_post_allowed({})
