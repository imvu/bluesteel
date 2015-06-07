""" Presenter views, main page functions """

from app.presenter.views import ViewHelper
from app.service.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.util.httpcommon.Page import Page
from app.util.httpcommon import res

LAYOUT_ITEMS_PER_PAGE = 3

def add_url_to_each_layout(layout_list):
    for layout in layout_list:
        layout['url'] = ViewHelper.create_edit_url_from_layout_id(layout['id'])

def get_main(request):
    """ Returns html for the main page """
    page = Page(LAYOUT_ITEMS_PER_PAGE, 1)
    layout_list = BluesteelLayoutEntry.objects.get_paginated_layouts_as_objects(page)
    add_url_to_each_layout(layout_list)

    data = {}
    data['layout_list'] = layout_list
    data['menu'] = []
    data['menu'].append({'name':'Main', 'link':'/main/view/'})
    data['menu'].append({'name':'Layout', 'link':'/main/layout/edit/0/'})
    data['create_layout'] = {}
    data['create_layout']['url'] = '/main/layout/create/'

    return res.get_template_data(request, 'presenter/main.html', data)
