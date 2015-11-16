""" Benchmark Execution Controller file """

from app.service.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.service.benchmark.models.BenchmarkExecutionModel import BenchmarkExecutionEntry
from app.service.gitrepo.models.GitCommitModel import GitCommitEntry
from app.util.commandrepo.models.CommandSetModel import CommandSetEntry

class BenchmarkExecutionController(object):
    """ BenchmarkExecution controller with helper functions """

    @staticmethod
    def get_earliest_available_execution():
        """
        Will return the earliest benchmark execution available to be executed.
        From all the definitions, we select the earliest commit with no execution or
        an execution that it is READY or INVALIDATED.
        It will return None if there is no execution available.
        """
        # This function might be very slow !!!

        bench_def_entries = BenchmarkDefinitionEntry.objects.all().order_by('created_at')
        bench_def_count = len(bench_def_entries)

        if bench_def_count == 0:
            return None

        commits = GitCommitEntry.objects.all().order_by('-author_date')

        for commit in commits:
            for bench_def in bench_def_entries:
                execution = BenchmarkExecutionEntry.objects.filter(commit=commit, definition=bench_def).first()
                if execution is None:
                    report = CommandSetEntry.objects.create(group=None)

                    entry = BenchmarkExecutionEntry.objects.create(
                        definition=bench_def,
                        commit=commit,
                        report=report,
                        revision_target=bench_def.revision,
                        status=BenchmarkExecutionEntry.IN_PROGRESS
                    )
                    return entry

                else:
                    inv = execution.invalidated
                    state = execution.status == BenchmarkExecutionEntry.READY
                    rev = execution.revision_target != bench_def.revision

                    if inv or state or rev:
                        execution.invalidated = False
                        execution.status = BenchmarkExecutionEntry.IN_PROGRESS
                        execution.revision_target = bench_def.revision
                        execution.save()
                        return execution

        return None

