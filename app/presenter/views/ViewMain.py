""" Presenter views, main page functions """

from app.service.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.util.httpcommon.Page import Page
from app.util.httpcommon import res

LAYOUT_ITEMS_PER_PAGE = 3

def get_main(request):
    """ Returns html for the main page """
    page = Page(LAYOUT_ITEMS_PER_PAGE, 1)
    layout_list = BluesteelLayoutEntry.objects.get_paginated_layouts_as_objects(page)

    data = {}
    data['layout_list'] = layout_list
    return res.get_template_data(request, 'presenter/main.html', data)
