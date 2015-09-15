""" Presenter views, Wrokers page functions """

from app.presenter.views import ViewUrlGenerator
from app.presenter.views import ViewPrepareObjects
from app.service.strongholdworker.models.WorkerModel import WorkerEntry
from app.util.commandrepo.models.CommandGroupModel import CommandGroupEntry
from app.util.httpcommon import res

def get_workers(request):
    """ Returns html for the workers page """
    if request.method == 'GET':
        worker_entries = WorkerEntry.objects.all()
        workers = []
        for entry in worker_entries:
            workers.append(entry.as_object())

        data = {}
        data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])
        data['workers'] = ViewPrepareObjects.prepare_workers_for_html(workers)
        data['download_worker'] = {}
        data['download_worker']['url'] = ViewUrlGenerator.get_download_worker_url()

        return res.get_template_data(request, 'presenter/workers.html', data)
    else:
        return res.get_only_get_allowed({})

def get_worker_reports(request, worker_id):
    """ Returns html for the worker reports page """
    if request.method == 'GET':
        workers = list(WorkerEntry.objects.filter(id=worker_id))
        if len(workers) == 0:
            return res.get_template_data(request, 'presenter/not_found.html', {})

        report_entries = list(CommandGroupEntry.objects.filter(user=workers[0].user))
        reports = []
        for report in report_entries:
            reports.append(report.as_object())

        data = {}
        data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])
        data['reports'] = ViewPrepareObjects.prepare_reports_for_html(reports)

        return res.get_template_data(request, 'presenter/worker_report.html', data)
    else:
        return res.get_only_get_allowed({})
