""" Benchmark Execution Controller file """

from django.db.models import Q, F
from app.logic.benchmark.models.BenchmarkExecutionModel import BenchmarkExecutionEntry
from app.logic.bluesteelworker.models.WorkerModel import WorkerEntry
from app.logic.commandrepo.models.CommandGroupModel import CommandGroupEntry
from app.logic.commandrepo.models.CommandSetModel import CommandSetEntry
from app.logic.commandrepo.controllers.CommandController import CommandController

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
    def delete_benchmark_executions(benchmark_definition):
        """ Deletes benchmark executions based on benchmark definitions """

        exec_entries = BenchmarkExecutionEntry.objects.filter(definition=benchmark_definition)

        for exec_entry in exec_entries:
            CommandController.delete_command_group_by_id(exec_entry.report.group.id)
            exec_entry.delete()

