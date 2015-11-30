""" Presenter json views, benchmark definition page functions """

from app.presenter.views import ViewUrlGenerator
from app.service.benchmark.controllers.BenchmarkDefinitionController import BenchmarkDefinitionController
from app.service.benchmark.views import BenchmarkDefinitionSchemas
from app.util.httpcommon import res, val

def create_new_benchmark_definition(request):
    """ Creates a new benchmark defintion """
    if request.method == 'POST':

        BenchmarkDefinitionController.create_default_benchmark_definition()

        data = {}
        data['redirect'] = ViewUrlGenerator.get_benchmark_definitions_url()

        return res.get_response(200, 'Benchmark definition created', data)
    else:
        return res.get_response(400, 'Only post allowed', {})


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
            layout_id=val_resp_obj['layout_id'],
            project_id=val_resp_obj['project_id'],
            command_list=val_resp_obj['command_list']
        )

        if bench_entry == None:
            return res.get_response(404, 'Benchmark Defintion save error', {})
        else:
            return res.get_response(200, 'Benchmark Definition saved', {})
    else:
        return res.get_only_post_allowed({})
