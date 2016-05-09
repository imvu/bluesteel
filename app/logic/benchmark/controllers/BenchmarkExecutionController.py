""" Benchmark Execution Controller file """

from django.db.models import Q, F
from django.core.paginator import Paginator
from app.logic.benchmark.models.BenchmarkExecutionModel import BenchmarkExecutionEntry
from app.logic.bluesteelworker.models.WorkerModel import WorkerEntry
from app.logic.commandrepo.models.CommandGroupModel import CommandGroupEntry
from app.logic.commandrepo.models.CommandSetModel import CommandSetEntry
from app.logic.commandrepo.models.CommandModel import CommandEntry
from app.logic.commandrepo.models.CommandResultModel import CommandResultEntry
from app.logic.commandrepo.controllers.CommandController import CommandController
from app.logic.gitrepo.controllers.GitController import GitController
from app.logic.gitrepo.models.GitBranchTrailModel import GitBranchTrailEntry
from app.logic.gitrepo.models.GitBranchMergeTargetModel import GitBranchMergeTargetEntry
from app.logic.httpcommon import pag
import json
import sys

PAGINATION_HALF_RANGE = 2

class BenchmarkExecutionController(object):
    """ BenchmarkExecution controller with helper functions """

    @staticmethod
    def get_earliest_available_execution(worker_user):
        """ Returns the earliest available execution possible """
        if worker_user.is_anonymous():
            return None

        worker_entry = WorkerEntry.objects.filter(user=worker_user).first()
        if worker_entry is None:
            return None

        q_ready = Q(status=BenchmarkExecutionEntry.READY)
        q_invalidated = Q(invalidated=True)
        q_revision = ~Q(revision_target=F('definition__revision'))

        execution = BenchmarkExecutionEntry.objects.filter(
            worker=worker_entry).filter(q_ready | q_invalidated | q_revision).order_by('-created_at').first()

        if execution is None:
            return None
        else:
            execution.invalidated = False
            execution.status = BenchmarkExecutionEntry.IN_PROGRESS
            execution.revision_target = execution.definition.revision
            execution.save()
            return execution

    @staticmethod
    def get_bench_exec_commits_paginated(project_entry, branch_entry, page):
        """ Returns a commit list window from a page """
        branch_trails = GitBranchTrailEntry.objects.filter(project=project_entry, branch=branch_entry).order_by('order')

        pager = Paginator(branch_trails, page.items_per_page)
        current_page = pager.page(page.page_index)
        branch_trails = current_page.object_list
        page_indices = pag.get_pagination_indices(page, PAGINATION_HALF_RANGE, pager.num_pages)

        commit_hashes = []
        for trail in branch_trails:
            commit_hashes.append(trail.commit.commit_hash)
        return (commit_hashes, page_indices)


    @staticmethod
    def get_stacked_executions_from_branch(project_entry, branch_entry, commit_hashes, bench_def_entry, worker_entry):
        """ Returns all benchmarks for a given branch """
        bench_data = []

        fork_point_hash = ''
        past_fork_point = False

        merge_target = GitBranchMergeTargetEntry.objects.filter(
            project=project_entry,
            current_branch=branch_entry).first()

        if merge_target and merge_target.current_branch != merge_target.target_branch:
            fork_point_hash = merge_target.fork_point.commit_hash

        for commit_hash in commit_hashes:
            benchmark_entry = BenchmarkExecutionEntry.objects.filter(
                definition=bench_def_entry,
                commit__commit_hash=commit_hash,
                worker=worker_entry
            ).first()

            slot = {}
            slot['exists'] = False
            slot['benchmark_execution_id'] = 0
            slot['results'] = {}
            slot['invalidated'] = False
            slot['current_branch'] = False
            slot['commit'] = ''

            if not benchmark_entry:
                bench_data.append(slot)
                continue

            if fork_point_hash == benchmark_entry.commit.commit_hash:
                past_fork_point = True

            slot['exists'] = True
            slot['benchmark_execution_id'] = benchmark_entry.id
            slot['results'] = benchmark_entry.get_benchmark_results()
            slot['invalidated'] = benchmark_entry.is_invalidated()
            slot['current_branch'] = not past_fork_point
            slot['commit'] = benchmark_entry.commit.commit_hash
            bench_data.append(slot)
        return list(reversed(bench_data))



    @staticmethod
    def get_stacked_data_separated_by_id(stacked_benchmark_data):
        """ Returns all benchmarks for a given branch """

        bench_data = {}
        for index, data in enumerate(stacked_benchmark_data):
            if not data['exists']:
                continue

            for exec_item in data['results']:
                if exec_item['visual_type'] != 'vertical_bars':
                    continue

                if exec_item['id'] not in bench_data:
                    bench_data[exec_item['id']] = [{
                        'average' : 0.0,
                        'benchmark_execution_id' : 0,
                        'bar_type' : 'invalidated'
                    }] * len(stacked_benchmark_data)

                obj = {}
                obj['average'] = exec_item['average']
                obj['benchmark_execution_id'] = data['benchmark_execution_id']
                obj['invalidated'] = data['invalidated']
                if data['current_branch']:
                    obj['bar_type'] = 'current_branch'
                else:
                    obj['bar_type'] = 'other_branch'
                bench_data[exec_item['id']][index] = obj

        return bench_data



    @staticmethod
    def create_benchmark_execution(definition, commit, worker):
        """ Creates a benchmark execution only if there is none equal before """
        command_group = CommandGroupEntry.objects.create()
        command_set = CommandSetEntry.objects.create(group=command_group)

        exec_entry = BenchmarkExecutionEntry.objects.filter(definition=definition, commit=commit, worker=worker).first()

        if not exec_entry:
            exec_entry = BenchmarkExecutionEntry.objects.create(
                definition=definition,
                commit=commit,
                worker=worker,
                report=command_set,
            )
        return exec_entry

    @staticmethod
    def create_bench_executions_from_commit(commit_entry, bench_def_entries, worker_entries):
        """ Create all the executions necessary from a given commit, definitions and workers """
        for bench_def in bench_def_entries:
            for worker in worker_entries:
                BenchmarkExecutionController.create_benchmark_execution(bench_def, commit_entry, worker)

    @staticmethod
    def create_bench_executions_from_worker(worker_entry, commit_entries, bench_def_entries):
        """ Create all the executions necessary from a given worker, definitions and commits """
        for bench_def in bench_def_entries:
            for commit in commit_entries:
                BenchmarkExecutionController.create_benchmark_execution(bench_def, commit, worker_entry)

    @staticmethod
    def create_bench_executions_from_definition(bench_def_entry, commit_entries, worker_entries):
        """ Create all the executions necessary from a given worker, definitions and commits """
        for worker in worker_entries:
            for commit in commit_entries:
                BenchmarkExecutionController.create_benchmark_execution(bench_def_entry, commit, worker)

    @staticmethod
    def save_bench_execution(bench_exec_entry, data):
        """ Save the report inside the benchmark execution without deleting command set object """
        CommandController.delete_commands_of_command_set(bench_exec_entry.report)

        for index, command in enumerate(data['command_set']):
            command_entry = CommandEntry.objects.create(
                command_set=bench_exec_entry.report,
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

        bench_exec_entry.status = BenchmarkExecutionEntry.FINISHED
        bench_exec_entry.save()

    @staticmethod
    def delete_benchmark_executions(benchmark_definition):
        """ Deletes benchmark executions based on benchmark definitions """

        exec_entries = BenchmarkExecutionEntry.objects.filter(definition=benchmark_definition)

        for exec_entry in exec_entries:
            CommandController.delete_command_group_by_id(exec_entry.report.group.id)
            exec_entry.delete()

    @staticmethod
    def add_bench_exec_completed_to_branches(branches):
        """ Iterates over branches and add how completed a commit is """

        for branch in branches:
            for commit in branch['commits']:
                count = BenchmarkExecutionEntry.objects.filter(commit__commit_hash=commit['hash']).count()

                finished = BenchmarkExecutionEntry.objects.filter(
                    commit__commit_hash=commit['hash'],
                    invalidated=False,
                    status=BenchmarkExecutionEntry.FINISHED,
                    revision_target=F('definition__revision')
                ).count()

                if count == 0:
                    commit['benchmark_completed'] = 0
                else:
                    commit['benchmark_completed'] = int((float(finished) / float(count)) * 100.0)

        return branches

    @staticmethod
    def get_benchmark_fluctuation(project, commit_hash, fluctuation_window):
        """ Returns fluctuation information from a commit range """
        hashes = GitController.get_commit_hashes_parents_and_children(project, commit_hash, fluctuation_window)
        benchmarks = {}
        fluctuations = []

        for commit_hash in hashes:
            bench = BenchmarkExecutionEntry.objects.filter(commit__commit_hash=commit_hash).first()
            if not bench:
                continue

            results = bench.get_benchmark_results()
            for result in results:
                if result['id'] not in benchmarks:
                    benchmarks[result['id']] = []
                benchmarks[result['id']].append(result)

        for key in benchmarks:
            average_min = sys.float_info.max
            average_max = sys.float_info.min

            need_append = False

            for bench in benchmarks[key]:
                if bench['visual_type'] == 'vertical_bars':
                    need_append = True
                    average_min = min(average_min, bench['average'])
                    average_max = max(average_max, bench['average'])

            if need_append:
                fluctuation = {}
                fluctuation['id'] = key
                fluctuation['min'] = average_min
                fluctuation['max'] = average_max
                fluctuations.append(fluctuation)

        return fluctuations




