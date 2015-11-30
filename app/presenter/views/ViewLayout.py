""" Presenter views, layout page functions """

from app.presenter.views.helpers import ViewUrlGenerator
from app.presenter.views.helpers import ViewPrepareObjects
from app.service.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.service.bluesteel.controllers.BluesteelLayoutController import BluesteelLayoutController
from app.util.httpcommon.Page import Page
from app.util.httpcommon import res

LAYOUT_ITEMS_PER_PAGE = 30

def get_layouts(request):
    """ Returns html for the layout page """
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

    return res.get_template_data(request, 'presenter/layout.html', data)

def get_layout_editable(request, layout_id):
    """ Returns html for the layout editable page """
    if request.method == 'GET':
        layout = BluesteelLayoutEntry.objects.all().filter(id=layout_id).first()

        data = {}
        data['layout'] = layout.as_object()
        data['layout'] = ViewPrepareObjects.prepare_layout_for_html(data['layout'])
        data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])

        for project in data['layout']['projects']:
            project = ViewPrepareObjects.prepare_project_for_html(project)

        return res.get_template_data(request, 'presenter/layout_edit.html', data)
    else:
        return res.get_template_data(request, 'presenter/not_found.html', {})

