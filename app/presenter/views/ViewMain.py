""" Presenter views, main page functions """

from app.presenter.views.helpers import ViewPrepareObjects
from app.util.httpcommon import res

def get_main(request):
    """ Returns html for the main page """

    data = {}
    data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])

    return res.get_template_data(request, 'presenter/main.html', data)
