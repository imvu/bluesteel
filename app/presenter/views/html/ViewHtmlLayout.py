""" Presenter views, layout page functions """

from app.presenter.views.helpers import ViewUrlGenerator
from app.presenter.views.helpers import ViewPrepareObjects
from app.logic.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.logic.bluesteel.controllers.BluesteelLayoutController import BluesteelLayoutController
from app.logic.httpcommon.Page import Page
from app.logic.httpcommon import res, pag

LAYOUT_ITEMS_PER_PAGE = 30

def get_layouts(request, page_index):
    """ Returns html for the layout page """
    page = Page(LAYOUT_ITEMS_PER_PAGE, page_index)
    layout_list, page_indices = BluesteelLayoutController.get_paginated_layouts_as_objects(page)

    for layout in layout_list:
        layout = ViewPrepareObjects.prepare_layout_for_html(layout)

    control = {}
    control['name'] = '  Add Layout'
    control['link'] = ViewUrlGenerator.get_layout_create_url()
    control['icon'] = 'fa fa-plus'
    control['onclick'] = 'executeAndRedirect(\'{0}\', \'\');'.format(control['link'])

    pagination = pag.get_pagination_urls(page_indices, ViewUrlGenerator.get_layout_all_url())

    print pagination

    data = {}
    data['layout_list'] = layout_list
    data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])
    data['pagination'] = pagination
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

def confirm_delete(request, layout_id):
    """ Confirm layout deletion """
    if request.method == 'GET':
        layout_entry = BluesteelLayoutEntry.objects.filter(id=layout_id).first()
        if layout_entry == None:
            return res.get_response(404, 'Bluesteel layout not found', {})

        data = {}
        data['confirm'] = {}
        data['confirm']['title'] = 'Delete layout'
        data['confirm']['text'] = 'Are you sure you want to delete this Layout ?'
        data['confirm']['url'] = {}
        data['confirm']['url']['accept'] = ViewUrlGenerator.get_delete_layout_url(layout_entry.id)
        data['confirm']['url']['cancel'] = ViewUrlGenerator.get_layout_edit_url(layout_entry.id)
        data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])

        return res.get_template_data(request, 'presenter/confirm.html', data)
    else:
        return res.get_only_get_allowed({})

