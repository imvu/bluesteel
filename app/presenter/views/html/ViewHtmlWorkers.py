""" Presenter views, Wrokers page functions """

from django.core.paginator import Paginator
from app.presenter.views.helpers import ViewUrlGenerator
from app.presenter.views.helpers import ViewPrepareObjects
from app.logic.benchmark.models.BenchmarkExecutionModel import BenchmarkExecutionEntry
from app.logic.bluesteelworker.models.WorkerModel import WorkerEntry
from app.logic.commandrepo.models.CommandGroupModel import CommandGroupEntry
from app.logic.httpcommon import res, pag
from app.logic.httpcommon.Page import Page

WORKER_ITEMS_PER_PAGE = 6
PAGINATION_HALF_RANGE = 2
MAX_LATEST_BENCHMARKS = 5

def get_workers_with_benchmark_info(worker_entries):
    """ Returns a list of workers with additional urls associated with those workers """
    workers = []
    for entry in worker_entries:
        wrk = entry.as_object()
        wrk['latest_benchmarks'] = []

        bench_execs = BenchmarkExecutionEntry.objects.filter(
            worker__id=entry.id,
            status=BenchmarkExecutionEntry.FINISHED
        ).order_by('-updated_at')[:MAX_LATEST_BENCHMARKS]

        for bench in bench_execs:
            bench_info = {}
            bench_info['id'] = bench.id
            bench_info['url'] = ViewUrlGenerator.get_benchmark_execution_complete_url(bench.id)
            wrk['latest_benchmarks'].append(bench_info)

        workers.append(wrk)

    return workers

def get_workers(request, page_index):
    """ Returns html for the workers page """
    if request.method == 'GET':
        worker_entries = WorkerEntry.objects.all()

        page = Page(WORKER_ITEMS_PER_PAGE, page_index)
        pager = Paginator(worker_entries, page.items_per_page)
        current_page = pager.page(page.page_index)
        worker_entries = current_page.object_list
        page_indices = pag.get_pagination_indices(page, PAGINATION_HALF_RANGE, pager.num_pages)

        workers = get_workers_with_benchmark_info(worker_entries)

        control = {}
        control['name'] = '  Download Worker'
        control['link'] = ViewUrlGenerator.get_download_worker_url()
        control['icon'] = 'fa fa-arrow-down'
        control['onclick'] = 'window.location="{0}"'.format(control['link'])

        pagination = ViewPrepareObjects.prepare_pagination_workers(page_indices)

        data = {}
        data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])
        data['pagination'] = pagination
        data['workers'] = ViewPrepareObjects.prepare_workers_for_html(workers)
        data['controls'] = []
        data['controls'].append(control)

        return res.get_template_data(request, 'presenter/workers.html', data)
    else:
        return res.get_only_get_allowed({})

def get_worker_edit(request, worker_id):
    """ Returns worker edit page to modify some workers properties """
    if request.method == 'GET':
        worker_entry = WorkerEntry.objects.filter(id=worker_id).first()
        if not worker_entry:
            return res.get_template_data(request, 'presenter/not_found.html', {})

        data = {}
        data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])
        data['worker'] = worker_entry.as_object()
        data['worker']['url'] = {}
        data['worker']['url']['save'] = ViewUrlGenerator.get_worker_save_url(worker_id)

        return res.get_template_data(request, 'presenter/worker_edit.html', data)
    else:
        return res.get_only_get_allowed({})

def get_worker_reports(request, worker_id):
    """ Returns html for the worker reports page """
    if request.method == 'GET':
        worker = WorkerEntry.objects.filter(id=worker_id).first()
        if not worker:
            return res.get_template_data(request, 'presenter/not_found.html', {})

        report_entries = CommandGroupEntry.objects.filter(user=worker.user)
        reports = []
        for report in report_entries:
            reports.append(report.as_object())

        data = {}
        data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])
        data['reports'] = ViewPrepareObjects.prepare_reports_for_html(reports)

        return res.get_template_data(request, 'presenter/worker_report.html', data)
    else:
        return res.get_only_get_allowed({})
