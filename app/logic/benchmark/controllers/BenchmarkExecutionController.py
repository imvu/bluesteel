""" Benchmark Execution Controller file """

from django.db.models import Q, F
from app.logic.benchmark.models.BenchmarkExecutionModel import BenchmarkExecutionEntry
from app.logic.bluesteelworker.models.WorkerModel import WorkerEntry

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


