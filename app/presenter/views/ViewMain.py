""" Presenter views, main page functions """

from django.http import HttpResponse
from django.template import RequestContext, loader
from app.service.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.util.httpcommon.Page import Page

LAYOUT_ITEMS_PER_PAGE = 3

def get_main(request):
    """ Returns html for the main page """
    page = Page(LAYOUT_ITEMS_PER_PAGE, 1)
    layout_list = BluesteelLayoutEntry.objects.get_paginated_layouts_as_objects(page)

    data = {}
    data['layout_list'] = layout_list

    template = loader.get_template('presenter/main.html')
    context = RequestContext(
        request,
        data,
    )

    response = HttpResponse(template.render(context))
    return response
