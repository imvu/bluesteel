""" Benchmark Execution Controller file """

import json
from datetime import timedelta
from django.db.models import Q, F, Count
from django.core.paginator import Paginator
from django.utils import timezone
from django.conf import settings
from app.logic.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.logic.benchmark.models.BenchmarkExecutionModel import BenchmarkExecutionEntry
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.logic.bluesteelworker.models.WorkerModel import WorkerEntry
from app.logic.commandrepo.models.CommandSetModel import CommandSetEntry
from app.logic.commandrepo.models.CommandModel import CommandEntry
from app.logic.commandrepo.models.CommandResultModel import CommandResultEntry
from app.logic.commandrepo.controllers import CommandController
from app.logic.gitrepo.controllers.GitController import GitController
from app.logic.gitrepo.models.GitProjectModel import GitProjectEntry
from app.logic.gitrepo.models.GitBranchModel import GitBranchEntry
from app.logic.gitrepo.models.GitCommitModel import GitCommitEntry
from app.logic.gitrepo.models.GitParentModel import GitParentEntry
from app.logic.gitrepo.models.GitBranchTrailModel import GitBranchTrailEntry
from app.logic.gitrepo.models.GitBranchMergeTargetModel import GitBranchMergeTargetEntry
from app.logic.httpcommon import pag
import arrow
import pytz

PAGINATION_HALF_RANGE = 2
TTL_IN_PROGRESS = 3

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

        time_to_live = timezone.now() - timedelta(hours=TTL_IN_PROGRESS)

        q_ready = Q(status=BenchmarkExecutionEntry.READY)
        q_invalidated = Q(invalidated=True)
        q_revision = ~Q(revision_target=F('definition__revision'))
        q_in_progress = Q(status=BenchmarkExecutionEntry.IN_PROGRESS, updated_at__lt=time_to_live)

        execution = (BenchmarkExecutionEntry.objects
                     .filter(definition__active=True)
                     .filter(definition__layout__active=True)
                     .filter(
                         definition__worker_pass_definition__allowed=True,
                         definition__worker_pass_definition__worker=worker_entry)
                     .filter(worker=worker_entry)
                     .filter(q_ready | q_invalidated | q_revision | q_in_progress)
                     .order_by('-commit__author_date')
                     .first())

        if execution is None:
            return None
        else:
            execution.invalidated = False
            execution.status = BenchmarkExecutionEntry.IN_PROGRESS
            execution.revision_target = execution.definition.revision
            execution.save()
            return execution

    @staticmethod
    def get_benchmark_execution_window(bench_exec_entry, window_half_apperture):
        """ Returns a list of stacked executions centered on a specific benchmark execution """
        project = GitProjectEntry.objects.filter(id=bench_exec_entry.definition.project.id).first()

        if not project:
            return {}

        commits_hashes = GitController.get_commit_hashes_parents_and_children(
            project=project,
            commit_hash=bench_exec_entry.commit.commit_hash,
            parents_children_count=window_half_apperture
        )

        branch_name = GitController.get_best_branch_from_a_commit(
            project_entry=project,
            commit_hash=bench_exec_entry.commit.commit_hash
        )

        branch = GitBranchEntry.objects.filter(project=project, name=branch_name).first()

        if not branch:
            print 'No best branch found!'
            return {}

        commits_hashes = list(reversed(commits_hashes))

        data_exec = BenchmarkExecutionController.get_stacked_executions_from_branch(
            project,
            branch,
            commits_hashes,
            bench_exec_entry.definition,
            bench_exec_entry.worker
        )

        return BenchmarkExecutionController.get_stacked_data_separated_by_id(data_exec)


    @staticmethod
    def get_bench_execs_ordered_by_worker(commit_entry):
        """ Returns a list of executions, ordered by worker, from a given commit """
        entries = BenchmarkExecutionEntry.objects.filter(commit__id=commit_entry.id).order_by('worker__id')

        ret = {}
        ret['commit'] = commit_entry.as_object()
        ret['commit']['parent'] = {}
        ret['commit']['parent']['id'] = None
        ret['commit']['son'] = {}
        ret['commit']['son']['id'] = None

        p_parent = GitParentEntry.objects.filter(project=commit_entry.project, son=commit_entry).first()
        p_son = GitParentEntry.objects.filter(project=commit_entry.project, parent=commit_entry).first()

        if p_parent:
            ret['commit']['parent']['id'] = p_parent.parent.id

        if p_son:
            ret['commit']['son']['id'] = p_son.son.id


        ret['workers'] = {}
        for entry in entries:
            bench_exec = {}
            bench_exec['id'] = entry.id
            bench_exec['name'] = entry.definition.name

            if entry.worker.id not in ret['workers']:
                obj = {}
                obj['worker'] = {}
                obj['worker']['id'] = entry.worker.id
                obj['worker']['name'] = entry.worker.name
                obj['worker']['uuid'] = entry.worker.uuid
                obj['worker']['operative_system'] = entry.worker.operative_system
                obj['executions'] = []
                obj['executions'].append(bench_exec)
                ret['workers'][entry.worker.id] = obj
            else:
                ret['workers'][entry.worker.id]['executions'].append(bench_exec)

        worker_list = []
        for worker_id in ret['workers']:
            worker_list.append(ret['workers'][worker_id])

        ret['workers'] = worker_list

        return ret


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
            slot['benchmark_execution_hash'] = ''
            slot['results'] = {}
            slot['invalidated'] = False
            slot['current_branch'] = False
            slot['commit'] = ''
            slot['status'] = 'Ready'

            if not benchmark_entry:
                bench_data.append(slot)
                continue

            if fork_point_hash == benchmark_entry.commit.commit_hash:
                past_fork_point = True

            slot['exists'] = True
            slot['benchmark_execution_id'] = benchmark_entry.id
            slot['benchmark_execution_hash'] = benchmark_entry.commit.commit_hash[:5]
            slot['results'] = benchmark_entry.get_benchmark_results()
            slot['invalidated'] = benchmark_entry.is_invalidated()
            slot['current_branch'] = not past_fork_point
            slot['commit'] = benchmark_entry.commit.commit_hash
            slot['status'] = benchmark_entry.get_status()
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
                        'median' : 0.0,
                        'benchmark_execution_id' : 0,
                        'benchmark_execution_hash' : '',
                        'bar_type' : 'invalidated',
                        'invalidated' : False,
                        'status' : 'Ready',
                    }] * len(stacked_benchmark_data)

                obj = {}
                obj['median'] = exec_item['median']
                obj['benchmark_execution_id'] = data['benchmark_execution_id']
                obj['benchmark_execution_hash'] = data['benchmark_execution_hash']
                obj['invalidated'] = data['invalidated']
                obj['status'] = data['status']
                if data['current_branch']:
                    obj['bar_type'] = 'current_branch'
                else:
                    obj['bar_type'] = 'other_branch'
                bench_data[exec_item['id']][index] = obj

        return bench_data



    @staticmethod
    def create_benchmark_execution(definition, commit, worker):
        """ Creates a benchmark execution only if there is none equal before """
        command_set = CommandSetEntry.objects.create()

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
    def create_bench_executions_from_commits(git_project_entry, commit_hashes):
        """ Create all the benchmark executions from a list of commits and its associate git project """
        project_entries = BluesteelProjectEntry.objects.filter(git_project=git_project_entry)
        bench_def_entries = BenchmarkDefinitionEntry.objects.filter(project__in=project_entries)
        worker_entries = WorkerEntry.objects.all()

        for commit_hash in commit_hashes:
            commit_entry = GitCommitEntry.objects.filter(commit_hash=commit_hash, project=git_project_entry).first()
            if not commit_entry:
                continue

            BenchmarkExecutionController.create_bench_executions_from_commit(
                commit_entry,
                bench_def_entries,
                worker_entries)

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
        CommandController.CommandController.delete_commands_of_command_set(bench_exec_entry.report)

        without_errors = True

        for index, command in enumerate(data['command_set']):
            command_entry = CommandEntry.objects.create(
                command_set=bench_exec_entry.report,
                command=command['command'],
                order=index)

            result = command['result']

            without_errors = without_errors and (int(result['status']) is 0)

            start_time = arrow.get(result['start_time']).naive
            finish_time = arrow.get(result['finish_time']).naive

            start_time = timezone.make_aware(start_time)
            finish_time = timezone.make_aware(finish_time, pytz.timezone(settings.TIME_ZONE), is_dst=False)

            CommandResultEntry.objects.create(
                command=command_entry,
                out=json.dumps(result['out']),
                error=result['error'],
                status=result['status'],
                start_time=start_time,
                finish_time=finish_time)

        if without_errors:
            bench_exec_entry.status = BenchmarkExecutionEntry.FINISHED
        else:
            bench_exec_entry.status = BenchmarkExecutionEntry.FINISHED_WITH_ERRORS
        bench_exec_entry.save()

    @staticmethod
    def delete_benchmark_executions(benchmark_definition):
        """ Deletes benchmark executions based on benchmark definitions """

        exec_entries = BenchmarkExecutionEntry.objects.filter(definition=benchmark_definition)

        for exec_entry in exec_entries:
            CommandController.CommandController.delete_command_set_by_id(exec_entry.report.id)
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
                    status__in=[BenchmarkExecutionEntry.FINISHED, BenchmarkExecutionEntry.FINISHED_WITH_ERRORS],
                    revision_target=F('definition__revision')
                ).count()

                if count == 0:
                    commit['benchmark_completed'] = 0
                else:
                    commit['benchmark_completed'] = int((float(finished) / float(count)) * 100.0)

        return branches

    @staticmethod
    def is_benchmark_young_for_notifications(benchmark_exec_entry):
        """ Returns true if benchmark is younger than max weeks for notify """
        max_weeks_old_notify = benchmark_exec_entry.definition.max_weeks_old_notify

        if max_weeks_old_notify < 0:
            return True

        now_date = timezone.now()
        author_date = benchmark_exec_entry.commit.author_date

        delta = now_date - author_date

        return (float(delta.days) / 7.0) < float(max_weeks_old_notify)

    @staticmethod
    def try_populate_benchmark_executions(project, count):
        """ We try to list all the non-yet-created benchmark executions, select a few of them, and construct them """
        all_workers = WorkerEntry.objects.all()
        all_defs = BenchmarkDefinitionEntry.objects.filter(project__git_project=project)

        workers_count = all_workers.count()
        defs_count = all_defs.count()
        permut = workers_count * defs_count

        entries = (GitCommitEntry.objects
                   .filter(project=project)
                   .annotate(Count('benchmark_exec_commit'))
                   .filter(benchmark_exec_commit__count__lt=permut)
                   .order_by('-author_date')[:count])

        created_count = 0
        for ent in entries:
            for bench_def in all_defs:
                for worker in all_workers:
                    if not BenchmarkExecutionEntry.objects.filter(
                            commit=ent,
                            definition=bench_def,
                            worker=worker).exists():
                        report = CommandSetEntry.objects.create(group=None)
                        BenchmarkExecutionEntry.objects.create(
                            commit=ent,
                            definition=bench_def,
                            worker=worker,
                            report=report)
                        created_count = created_count + 1

        return created_count

    @staticmethod
    def try_populate_executions(count):
        """ Tries to populate benchmark executions across all the git projects """
        projects = GitProjectEntry.objects.all()

        created = 0
        for project in projects:
            created = created + BenchmarkExecutionController.try_populate_benchmark_executions(project, count)

        return created
