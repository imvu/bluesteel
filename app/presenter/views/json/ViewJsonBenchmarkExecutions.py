""" Presenter json views, benchmark execution page functions """

from collections import defaultdict
from django.db import transaction
from django.utils import timezone
from app.presenter.schemas import BenchmarkExecutionSchemas
from app.presenter.views.helpers import ViewNotifications
from app.presenter.views.helpers import ViewPrepareObjects
from app.logic.benchmark.models.BenchmarkExecutionModel import BenchmarkExecutionEntry
from app.logic.benchmark.models.BenchmarkFluctuationWaiverModel import BenchmarkFluctuationWaiverEntry
from app.logic.benchmark.controllers.BenchmarkExecutionController import BenchmarkExecutionController
from app.logic.benchmark.controllers.BenchmarkFluctuationController import BenchmarkFluctuationController
from app.logic.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.logic.gitrepo.models.GitProjectModel import GitProjectEntry
from app.logic.gitrepo.models.GitBranchModel import GitBranchEntry
from app.logic.bluesteelworker.models.WorkerModel import WorkerEntry
from app.logic.httpcommon import res, val
from app.logic.httpcommon.Page import Page

FLUCTUATION_WINDOW = 2
BENCH_QUICK_DEFAULT_PAGE = 1
BENCH_QUICK_ITEMS = 30

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

def create_false_report(failure_type_text, extra_info):
    """ Generates a false report for cases where schema fails or json validation fails """
    result = {}
    result['id'] = failure_type_text
    result['visual_type'] = 'unknown'
    result['data'] = str(extra_info)

    com = {}
    com['command'] = 'Problem while saving benchmark execution!'
    com['result'] = {}
    com['result']['status'] = -1
    com['result']['out'] = []
    com['result']['out'].append(result)
    com['result']['error'] = ''
    com['result']['start_time'] = timezone.now()
    com['result']['finish_time'] = timezone.now()

    obj = {}
    obj['command_set'] = []
    obj['command_set'].append(com)
    return obj

@transaction.atomic
def save_benchmark_execution(request, benchmark_execution_id):
    """ Check and save a benchmark execution data into the db """
    if request.method == 'POST':
        bench_exec_entry = BenchmarkExecutionEntry.objects.filter(id=benchmark_execution_id).first()
        if bench_exec_entry is None:
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
            report = create_false_report('schema_failed', val_resp_obj)
            BenchmarkExecutionController.save_bench_execution(bench_exec_entry, report)
            return res.get_schema_failed(val_resp_obj)

        for command in val_resp_obj['command_set']:
            (ids_correct, ids) = check_benchmark_json_ids(command['result']['out'])
            if not ids_correct:
                data = {'out' : command['result']['out'], 'ids' : ids}
                return res.get_response(400, 'Benchmark ids are not correct', data)

        report = val_resp_obj
        BenchmarkExecutionController.save_bench_execution(bench_exec_entry, report)
        young_to_notify = BenchmarkExecutionController.is_benchmark_young_for_notifications(bench_exec_entry)

        if not did_commands_succeed(report) and young_to_notify:
            ViewNotifications.notify_benchmark_command_failure(
                bench_exec_entry.id,
                bench_exec_entry.commit.author.email,
                bench_exec_entry.commit.commit_hash,
                report,
                request.get_host()
            )

        allow_notifications = BenchmarkFluctuationWaiverEntry.objects.filter(
            git_project__id=bench_exec_entry.commit.project.id,
            git_user__id=bench_exec_entry.commit.author.id,
            notification_allowed=True
        ).exists()

        fluctuation_exist = BenchmarkFluctuationController.does_benchmark_fluctuation_exist(bench_exec_entry)

        if fluctuation_exist[0] and young_to_notify and allow_notifications:
            ViewNotifications.notify_benchmark_fluctuation(
                bench_exec_entry.id,
                bench_exec_entry.commit.as_object(),
                bench_exec_entry.worker.as_object(),
                bench_exec_entry.definition.name,
                request.get_host(),
                fluctuation_exist[1]
            )

        return res.get_response(200, 'Benchmark Execution saved', {})
    else:
        return res.get_response(400, 'Only post allowed', {})

@transaction.atomic
def invalidate_benchmark_execution(request, benchmark_execution_id):
    """ Check and save a benchmark execution data into the db """
    if request.method == 'POST':
        bench_exec_entry = BenchmarkExecutionEntry.objects.filter(id=benchmark_execution_id).first()
        if bench_exec_entry is None:
            return res.get_response(404, 'Bench Execution Entry not found', {})

        bench_exec_entry.invalidated = True
        bench_exec_entry.save()

        return res.get_response(200, 'Benchmark Execution invalidated', {})
    else:
        return res.get_response(400, 'Only post allowed', {})


def get_benchmark_executions_stacked_quick(request, project_id, branch_id, definition_id, worker_id):
    """ Returns benchmark executions stacked and paginated """
    if request.method == 'GET':
        project = BluesteelProjectEntry.objects.filter(id=project_id).first()
        if project is None:
            return res.get_response(404, 'BluesteelProject not found', {})

        git_project = GitProjectEntry.objects.filter(id=project.git_project.id).first()
        if git_project is None:
            return res.get_response(404, 'GitProject not found', {})

        branch = GitBranchEntry.objects.filter(id=branch_id, project=git_project).first()
        if branch is None:
            return res.get_response(404, 'GitBranchEntry not found', {})

        definition = BenchmarkDefinitionEntry.objects.filter(id=definition_id, project=project).first()
        if definition is None:
            return res.get_response(404, 'BenchmarkDefinitionEntry not found', {})

        worker = WorkerEntry.objects.filter(id=worker_id).first()
        if worker is None:
            return res.get_response(404, 'WorkerEntry not found', {})

        page = Page(BENCH_QUICK_ITEMS, BENCH_QUICK_DEFAULT_PAGE)
        commit_hashes_list, pagination = BenchmarkExecutionController.get_bench_exec_commits_paginated(
            git_project,
            branch,
            page
        )
        del pagination

        data_exec = BenchmarkExecutionController.get_stacked_executions_from_branch(
            git_project,
            branch,
            commit_hashes_list,
            definition,
            worker
        )

        exec_stacked = BenchmarkExecutionController.get_stacked_data_separated_by_id(data_exec)

        execs = ViewPrepareObjects.prepare_stacked_executions_url_field(request.get_host(), exec_stacked)
        execs = ViewPrepareObjects.prepare_stacked_executions_json_field(execs)

        data = {}
        data['stacked_executions'] = execs

        return res.get_response(200, 'Benchmark Execution Stacked', data)
    else:
        return res.get_only_get_allowed({})
