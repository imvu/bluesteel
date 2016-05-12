""" Presenter json views, benchmark execution page functions """

from app.presenter.schemas import BenchmarkExecutionSchemas
from app.presenter.views.helpers import ViewNotifications
from app.logic.benchmark.models.BenchmarkExecutionModel import BenchmarkExecutionEntry
from app.logic.benchmark.controllers.BenchmarkExecutionController import BenchmarkExecutionController
from app.logic.httpcommon import res, val
from collections import defaultdict

def check_benchmark_json_ids(report_out):
    """ Checks if the ids inside the report out fields are unique """
    ids = defaultdict(int)

    for obj in report_out:
        bench_id = '{0}-{1}'.format(obj['id'], obj['visual_type'])
        ids[bench_id] += 1

    for key, value in ids.iteritems():
        del key
        if value > 1:
            return (False, ids)
    return (True, ids)


def did_commands_succeed(report):
    """ Returns true if all the commands succeed"""
    for com in report['command_set']:
        if com['result']['status'] != 0:
            return False
    return True


def does_benchmark_fluctuation_exist(benchmark_exec_entry, fluctuation_window):
    """ Returns true if fluctuation exists """
    commit_hash = benchmark_exec_entry.commit.commit_hash
    fluctuations = BenchmarkExecutionController.get_benchmark_fluctuation(
        project=benchmark_exec_entry.definition.project,
        commit_hash=commit_hash,
        fluctuation_window=fluctuation_window
    )

    for fluc in fluctuations:
        if (float(fluc['max'] - fluc['min'])) > 1.0:
            return True
    return False


def save_benchmark_execution(request, benchmark_execution_id):
    """ Check and save a benchmark execution data into the db """
    if request.method == 'POST':
        bench_exec_entry = BenchmarkExecutionEntry.objects.filter(id=benchmark_execution_id).first()
        if bench_exec_entry == None:
            return res.get_response(404, 'Bench Execution Entry not found', {})

        (is_json_valid, post_info) = val.validate_json_string(request.body)
        if not is_json_valid:
            ViewNotifications.notify_json_invalid(bench_exec_entry.commit.author.email, request.body)
            return res.get_json_parser_failed({})

        (obj_validated, val_resp_obj) = val.validate_obj_schema(
            post_info,
            BenchmarkExecutionSchemas.SAVE_BENCHMARK_EXECUTION)
        if not obj_validated:
            ViewNotifications.notify_schema_failed(bench_exec_entry.commit.author.email, post_info, val_resp_obj)
            return res.get_schema_failed(val_resp_obj)

        for command in val_resp_obj['command_set']:
            (ids_correct, ids) = check_benchmark_json_ids(command['result']['out'])
            if not ids_correct:
                data = {'out' : command['result']['out'], 'ids' : ids}
                return res.get_response(400, 'Benchmark ids are not correct', data)

        report = val_resp_obj
        BenchmarkExecutionController.save_bench_execution(bench_exec_entry, report)

        if not did_commands_succeed(report):
            ViewNotifications.notify_benchmark_command_failure(
                bench_exec_entry.commit.author.email,
                bench_exec_entry.id,
                bench_exec_entry.commit.commit_hash,
                request.get_host()
            )

        if does_benchmark_fluctuation_exist(bench_exec_entry, 2):
            ViewNotifications.notify_benchmark_fluctuation(
                bench_exec_entry.commit.author.email,
                bench_exec_entry.id,
                bench_exec_entry.commit.commit_hash,
                request.get_host()
            )

        return res.get_response(200, 'Benchmark Execution saved', {})
    else:
        return res.get_response(400, 'Only post allowed', {})


def invalidate_benchmark_execution(request, benchmark_execution_id):
    """ Check and save a benchmark execution data into the db """
    if request.method == 'POST':
        bench_exec_entry = BenchmarkExecutionEntry.objects.filter(id=benchmark_execution_id).first()
        if bench_exec_entry == None:
            return res.get_response(404, 'Bench Execution Entry not found', {})

        bench_exec_entry.invalidated = True
        bench_exec_entry.save()

        return res.get_response(200, 'Benchmark Execution invalidated', {})
    else:
        return res.get_response(400, 'Only post allowed', {})
