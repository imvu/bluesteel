""" Presenter views, main page functions """

from app.presenter.views import ViewUrlGenerator
from app.presenter.views import ViewPrepareObjects
from app.service.bluesteel.controllers.BluesteelLayoutController import BluesteelLayoutController
from app.util.httpcommon.Page import Page
from app.util.httpcommon import res

LAYOUT_ITEMS_PER_PAGE = 30

def get_main(request):
    """ Returns html for the main page """
    page = Page(LAYOUT_ITEMS_PER_PAGE, 1)
    layout_list = BluesteelLayoutController.get_paginated_layouts_as_objects(page)

    for layout in layout_list:
        layout = ViewPrepareObjects.prepare_layout_for_html(layout)

    control = {}
    control['name'] = '  Add Layout'
    control['link'] = ViewUrlGenerator.get_layout_create_url()
    control['icon'] = 'fa fa-plus'
    control['onclick'] = 'create_new_layout(this, \'{0}\');'.format(control['link'])

    data = {}
    data['layout_list'] = layout_list
    data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])
    data['controls'] = []
    data['controls'].append(control)

    return res.get_template_data(request, 'presenter/main.html', data)
