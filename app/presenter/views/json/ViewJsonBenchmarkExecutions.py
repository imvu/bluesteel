""" Presenter json views, benchmark execution page functions """

from app.presenter.schemas import BenchmarkExecutionSchemas
from app.logic.benchmark.models.BenchmarkExecutionModel import BenchmarkExecutionEntry
from app.logic.commandrepo.controllers.CommandController import CommandController
from app.logic.commandrepo.models.CommandModel import CommandEntry
from app.logic.commandrepo.models.CommandSetModel import CommandSetEntry
from app.logic.commandrepo.models.CommandResultModel import CommandResultEntry
from app.logic.httpcommon import res, val
import json

def save_benchmark_execution(request, benchmark_execution_id):
    """ Check and save a benchmark execution data into the db """
    if request.method == 'POST':
        bench_exec_entry = BenchmarkExecutionEntry.objects.filter(id=benchmark_execution_id).first()
        if bench_exec_entry == None:
            return res.get_response(404, 'Bench Execution Entry not found', {})

        (is_json_valid, post_info) = val.validate_json_string(request.body)
        if not is_json_valid:
            return res.get_json_parser_failed({})

        (obj_validated, val_resp_obj) = val.validate_obj_schema(
            post_info,
            BenchmarkExecutionSchemas.SAVE_BENCHMARK_EXECUTION)
        if not obj_validated:
            return res.get_schema_failed(val_resp_obj)

        command_set = CommandSetEntry.objects.create()

        obj = val_resp_obj
        for index, command in enumerate(obj['command_set']):
            command_entry = CommandEntry.objects.create(
                command_set=command_set,
                command=command['command'],
                order=index)

            result = command['result']

            CommandResultEntry.objects.create(
                command=command_entry,
                out=json.dumps(result['out']),
                error=result['error'],
                status=result['status'],
                start_time=result['start_time'],
                finish_time=result['finish_time'])

        CommandController.delete_command_set_by_id(bench_exec_entry.report.id)
        bench_exec_entry.report = command_set
        bench_exec_entry.save()

        return res.get_response(200, 'Benchmark Execution saved', {})
    else:
        return res.get_response(400, 'Only post allowed', {})
