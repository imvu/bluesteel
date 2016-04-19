""" Presenter json views, benchmark execution page functions """

from django.conf import settings
from app.presenter.schemas import BenchmarkExecutionSchemas
from app.presenter.views.helpers import ViewUrlGenerator
from app.logic.mailing.models.StackedMailModel import StackedMailEntry
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


def notify_benchmark_fluctuation(benchmark_exec_entry, fluctuation_window, domain):
    """ It generates stacked email entries based on fluctuation notifications """
    commit_hash = benchmark_exec_entry.commit.commit_hash
    fluctuations = BenchmarkExecutionController.get_benchmark_fluctuation(
        project=benchmark_exec_entry.definition.project,
        commit_hash=commit_hash,
        fluctuation_window=fluctuation_window
    )

    notify_fluctuation = False

    for fluc in fluctuations:
        if (float(fluc['max'] - fluc['min'])) > 1.0:
            notify_fluctuation = True
            break

    if notify_fluctuation:
        receiver_email = benchmark_exec_entry.commit.author.email
        commit_hash = benchmark_exec_entry.commit.commit_hash
        title = 'Benchmark execution fluctuation on commit: {0}'.format(commit_hash)
        content = 'There were fluctuations on the benchmark execution.\nTake a look at: {0}'.format(
            ViewUrlGenerator.get_benchmark_execution_window_full_url(
                domain,
                benchmark_exec_entry.id)
            )

        StackedMailEntry.objects.create(
            sender=settings.DEFAULT_FROM_EMAIL,
            receiver=receiver_email,
            title=title,
            content=content
        )

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

        for command in val_resp_obj['command_set']:
            (ids_correct, ids) = check_benchmark_json_ids(command['result']['out'])
            if not ids_correct:
                data = {'out' : command['result']['out'], 'ids' : ids}
                return res.get_response(400, 'Benchmark ids are not correct', data)

        report = val_resp_obj
        BenchmarkExecutionController.save_bench_execution(bench_exec_entry, report)
        notify_benchmark_fluctuation(bench_exec_entry, 2, request.get_host())

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
