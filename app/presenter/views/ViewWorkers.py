""" Presenter views, Wrokers page functions """

from app.presenter.views import ViewUrlGenerator
from app.presenter.views import ViewPrepareObjects
from app.util.httpcommon import res

def get_workers(request):
    """ Returns html for the workers page """

    data = {}
    data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])
    data['download_worker'] = {}
    data['download_worker']['url'] = ViewUrlGenerator.get_download_worker_url()

    return res.get_template_data(request, 'presenter/workers.html', data)
