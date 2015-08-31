""" Presenter views, main page functions """

from app.presenter.views import ViewUrlGenerator
from app.presenter.views import ViewPrepareObjects
from app.service.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.util.httpcommon.Page import Page
from app.util.httpcommon import res

LAYOUT_ITEMS_PER_PAGE = 30

def get_main(request):
    """ Returns html for the main page """
    page = Page(LAYOUT_ITEMS_PER_PAGE, 1)
    layout_list = BluesteelLayoutEntry.objects.get_paginated_layouts_as_objects(page)

    for layout in layout_list:
        layout = ViewPrepareObjects.prepare_layout_for_html(layout)

    data = {}
    data['layout_list'] = layout_list
    data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])
    data['create_layout'] = {}
    data['create_layout']['url'] = ViewUrlGenerator.get_layout_create_url()

    return res.get_template_data(request, 'presenter/main.html', data)
