""" Prepare objects for template consumption """

from app.presenter.views import ViewUrlGenerator

def prepare_layout_for_html(layout):
    """ Adds information to layout objects for template interaction """
    layout['url'] = {}
    layout['url']['edit'] = ViewUrlGenerator.get_layout_edit_url(layout['id'])
    layout['url']['save'] = ViewUrlGenerator.get_save_layout_url(layout['id'])
    layout['url']['add_project'] = ViewUrlGenerator.get_add_default_project_url(layout['id'])

    obj_active = {}
    obj_active['name'] = 'ACTIVE'
    obj_active['value'] = 1
    obj_active['selected'] = ''

    obj_inactive = {}
    obj_inactive['name'] = 'INACTIVE'
    obj_inactive['value'] = 0
    obj_inactive['selected'] = ''

    if layout['active'] == True:
        obj_active['selected'] = 'selected'
    else:
        obj_inactive['selected'] = 'selected'

    layout['active_selection'] = []
    layout['active_selection'].append(obj_active)
    layout['active_selection'].append(obj_inactive)

    layout['project_selection'] = []
    for index, project in enumerate(layout['projects']):
        obj = {}
        obj['name'] = project['name']
        obj['value'] = index
        obj['selected'] = ''
        if int(index) == int(layout['project_index_path']):
            obj['selected'] = 'selected'

        layout['project_selection'].append(obj)

    return layout

def prepare_project_for_html(project):
    """ Adds information to project objects for template interaction """
    project['url'] = {}
    project['url']['save'] = ViewUrlGenerator.get_save_project_url(project['id'])
    project['url']['delete'] = ViewUrlGenerator.get_delete_project_url(project['id'])
    return project

def prepare_menu_for_html(menu):
    """ Adds default items to menu plus already existing ones """
    menu_items = []

    item_1 = {}
    item_1['name'] = ''
    item_1['icon'] = 'fa fa-home fa-lg'
    item_1['link'] = '/main/view/'

    item_2 = {}
    item_2['name'] = 'Worker'
    item_2['icon'] = ''
    item_2['link'] = '/bluesteelworker/download/'

    menu_items.append(item_1)
    menu_items.append(item_2)

    for item in menu:
        menu_items.append(item)

    return menu_items

