""" Presenter views, benchmark execution page functions """

from app.presenter.views.helpers import ViewPrepareObjects
from app.logic.benchmark.models.BenchmarkExecutionModel import BenchmarkExecutionEntry
from app.logic.httpcommon import res

def get_benchmark_execution(request, bench_exec_id):
    """ Returns a benchmark execution """
    data = {}
    data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])

    exec_entry = BenchmarkExecutionEntry.objects.filter(id=bench_exec_id).first()

    if exec_entry == None:
        return res.get_template_data(request, 'presenter/not_found.html', data)

    obj = exec_entry.as_object()
    data['execution'] = ViewPrepareObjects.prepare_benchmark_execution_for_html(obj)
    print data

    return res.get_template_data(request, 'presenter/benchmark_execution.html', data)
