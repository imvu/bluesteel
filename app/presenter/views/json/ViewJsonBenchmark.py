""" Bluesteel views functions """

from app.logic.benchmark.controllers.BenchmarkExecutionController import BenchmarkExecutionController
from app.logic.httpcommon import res

def acquire_benchmark_execution(request):
    """ Acquire the next available benchmark execution posible """
    if request.method == 'POST':
        next_execution = BenchmarkExecutionController.get_earliest_available_execution()

        if next_execution is None:
            return res.get_response(404, 'Next Execution not found', {})
        else:
            return res.get_response(200, 'Next Execution', next_execution.as_object())
    else:
        return res.get_only_post_allowed({})
