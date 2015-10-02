""" Prepare objects for template consumption """

from app.presenter.views import ViewUrlGenerator
import json

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
    item_2['name'] = 'Workers'
    item_2['icon'] = ''
    item_2['link'] = '/main/workers/'

    item_3 = {}
    item_3['name'] = 'Projects'
    item_3['icon'] = ''
    item_3['link'] = '/main/projects/'

    menu_items.append(item_1)
    menu_items.append(item_2)
    menu_items.append(item_3)

    for item in menu:
        menu_items.append(item)

    return menu_items


def prepare_workers_for_html(workers):
    """ Prepares workers for html template """
    worker_items = []

    for worker in workers:

        worker['last_update'] = str(worker['last_update'])
        worker['url'] = {}
        worker['url']['report'] = ViewUrlGenerator.get_worker_report_url(worker['id'])
        worker_items.append(worker)

    return worker_items

def prepare_reports_for_html(reports):
    """ Prepares reports for html template """
    report_items = []

    for report in reports:
        for com_set in report['command_sets']:
            for command in com_set['commands']:
                parts = json.loads(command['command'])
                command['command'] = ' '.join(parts)

        report_items.append(report)

    return report_items

def prepare_branches_for_html(project_id, branches):
    """ Prepare branch data adding urls before html """
    ret_branches = []
    for branch in branches:
        branch['url'] = {}
        branch['url']['single'] = ViewUrlGenerator.get_project_branch_single_url(project_id, branch['id'])
        ret_branches.append(branch)
    return ret_branches
