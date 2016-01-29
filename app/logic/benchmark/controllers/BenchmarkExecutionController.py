""" Benchmark Execution Controller file """

from django.db.models import Q, F
from app.logic.benchmark.models.BenchmarkExecutionModel import BenchmarkExecutionEntry
from app.logic.bluesteelworker.models.WorkerModel import WorkerEntry
from app.logic.commandrepo.models.CommandGroupModel import CommandGroupEntry
from app.logic.commandrepo.models.CommandSetModel import CommandSetEntry
from app.logic.commandrepo.models.CommandModel import CommandEntry
from app.logic.commandrepo.models.CommandResultModel import CommandResultEntry
from app.logic.commandrepo.controllers.CommandController import CommandController
from app.logic.gitrepo.models.GitBranchTrailModel import GitBranchTrailEntry
import json

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
    def get_benchmark_execution_from_branch(project_entry, branch_entry, bench_def_entry, worker_entry):
        """ Returns all benchmarks for a given branch """
        branch_trails = GitBranchTrailEntry.objects.filter(project=project_entry, branch=branch_entry).order_by('order')
        bench_data = {}

        for index, trail in enumerate(branch_trails):
            benchmark_entry = BenchmarkExecutionEntry.objects.filter(
                definition=bench_def_entry,
                commit=trail.commit,
                worker=worker_entry
            ).first()

            if not benchmark_entry:
                continue

            report_obj = benchmark_entry.report.as_object()

            for command in report_obj['commands']:
                out_obj = json.loads(command['result']['out'])
                for bench_res in out_obj:
                    if bench_res['visual_type'] == 'vertical_bars':
                        if bench_res['id'] not in bench_data:
                            bench_data[bench_res['id']] = []

                        slot = {}
                        slot['index'] = index
                        slot['data'] = bench_res['data']
                        slot['benchmark_execution_id'] = benchmark_entry.id
                        bench_data[bench_res['id']].append(slot)


        for key in bench_data:
            data = [{
                'average' : 0.0,
                'benchmark_execution_id' : 0
            }] * len(branch_trails)

            for slot in bench_data[key]:
                average = 0.0
                for value in slot['data']:
                    average += float(value)
                average = average / float(len(slot['data']))
                data[slot['index']] = {
                    'average' : average,
                    'benchmark_execution_id' : slot['benchmark_execution_id']
                }

            bench_data[key] = data

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

