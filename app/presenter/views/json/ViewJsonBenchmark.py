""" Bluesteel views functions """

from app.presenter.views.helpers import ViewPrepareObjects
from app.logic.benchmark.controllers.BenchmarkExecutionController import BenchmarkExecutionController
from app.logic.httpcommon import res

POPULATE_EXECUTIONS_INC_COUNT = 2

def acquire_benchmark_execution(request):
    """ Acquire the next available benchmark execution posible """
    if request.method == 'POST':
        BenchmarkExecutionController.try_populate_executions(POPULATE_EXECUTIONS_INC_COUNT)
        next_execution = BenchmarkExecutionController.get_earliest_available_execution(request.user)

        if next_execution is None:
            return res.get_response(404, 'Next Execution not found', {})
        else:
            execution = ViewPrepareObjects.prepare_benchmark_execution_for_html(
                next_execution.as_object(),
                request.get_host())
            return res.get_response(200, 'Next Execution', execution)
    else:
        return res.get_only_post_allowed({})
