""" Prepare objects for template consumption """

import json
from app.presenter.views.helpers import ViewUrlGenerator

def prepare_layout_for_html(layout):
    """ Adds information to layout objects for template interaction """
    layout['url'] = {}
    layout['url']['edit'] = ViewUrlGenerator.get_layout_edit_url(layout['id'])
    layout['url']['save'] = ViewUrlGenerator.get_save_layout_url(layout['id'])
    layout['url']['confirm_delete'] = ViewUrlGenerator.get_confirm_delete_layout_url(layout['id'])
    layout['url']['confirm_wipe'] = ViewUrlGenerator.get_confirm_wipe_layout_url(layout['id'])
    layout['url']['add_project'] = ViewUrlGenerator.get_add_default_project_url(layout['id'])

    obj_active = {}
    obj_active['name'] = 'ACTIVE'
    obj_active['value'] = 1
    obj_active['selected'] = ''

    obj_inactive = {}
    obj_inactive['name'] = 'INACTIVE'
    obj_inactive['value'] = 0
    obj_inactive['selected'] = ''

    if layout['active'] is True:
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

def prepare_pagination_layout(page_indices):
    """ Creates pagination object for layout from indices """
    pagination = {}
    pagination['prev'] = ViewUrlGenerator.get_layout_all_url(page_indices['prev'])
    pagination['current'] = ViewUrlGenerator.get_layout_all_url(page_indices['current'])
    pagination['next'] = ViewUrlGenerator.get_layout_all_url(page_indices['next'])

    pagination['pages'] = []
    for index in page_indices['page_indices']:
        pag = {}
        pag['index'] = index
        pag['url'] = ViewUrlGenerator.get_layout_all_url(index)
        pag['is_current'] = (index == page_indices['current'])
        pagination['pages'].append(pag)
    return pagination

def prepare_pagination_project(page_indices):
    """ Creates pagination object for project from indices """
    pagination = {}
    pagination['prev'] = ViewUrlGenerator.get_project_all_url(page_indices['prev'])
    pagination['current'] = ViewUrlGenerator.get_project_all_url(page_indices['current'])
    pagination['next'] = ViewUrlGenerator.get_project_all_url(page_indices['next'])

    pagination['pages'] = []
    for index in page_indices['page_indices']:
        pag = {}
        pag['index'] = index
        pag['url'] = ViewUrlGenerator.get_project_all_url(index)
        pag['is_current'] = (index == page_indices['current'])
        pagination['pages'].append(pag)
    return pagination

def prepare_pagination_branches(project_id, commit_depth, page_indices):
    """ Creates pagination object for branches from indices """
    pagination = {}
    pagination['prev'] = ViewUrlGenerator.get_project_branches_url(project_id, commit_depth, page_indices['prev'])
    pagination['current'] = ViewUrlGenerator.get_project_branches_url(project_id, commit_depth, page_indices['current'])
    pagination['next'] = ViewUrlGenerator.get_project_branches_url(project_id, commit_depth, page_indices['next'])

    pagination['pages'] = []
    for index in page_indices['page_indices']:
        pag = {}
        pag['index'] = index
        pag['url'] = ViewUrlGenerator.get_project_branches_url(project_id, commit_depth, index)
        pag['is_current'] = (index == page_indices['current'])
        pagination['pages'].append(pag)
    return pagination

def prepare_pagination_workers(page_indices):
    """ Creates pagination object for workers from indices """
    pagination = {}
    pagination['prev'] = ViewUrlGenerator.get_worker_all_url(page_indices['prev'])
    pagination['current'] = ViewUrlGenerator.get_worker_all_url(page_indices['current'])
    pagination['next'] = ViewUrlGenerator.get_worker_all_url(page_indices['next'])

    pagination['pages'] = []
    for index in page_indices['page_indices']:
        pag = {}
        pag['index'] = index
        pag['url'] = ViewUrlGenerator.get_worker_all_url(index)
        pag['is_current'] = (index == page_indices['current'])
        pagination['pages'].append(pag)
    return pagination

def prepare_pagination_feed_reports(worker_id, page_indices):
    """ Creates pagination object for workers from indices """
    pagination = {}
    pagination['prev'] = ViewUrlGenerator.get_feed_report_form_worker_url(worker_id, page_indices['prev'])
    pagination['current'] = ViewUrlGenerator.get_feed_report_form_worker_url(worker_id, page_indices['current'])
    pagination['next'] = ViewUrlGenerator.get_feed_report_form_worker_url(worker_id, page_indices['next'])

    pagination['pages'] = []
    for index in page_indices['page_indices']:
        pag = {}
        pag['index'] = index
        pag['url'] = ViewUrlGenerator.get_feed_report_form_worker_url(worker_id, index)
        pag['is_current'] = (index == page_indices['current'])
        pagination['pages'].append(pag)
    return pagination

def prepare_pagination_bench_definitions(page_indices):
    """ Creates pagination object for workers from indices """
    pagination = {}
    pagination['prev'] = ViewUrlGenerator.get_benchmark_definitions_url(page_indices['prev'])
    pagination['current'] = ViewUrlGenerator.get_benchmark_definitions_url(page_indices['current'])
    pagination['next'] = ViewUrlGenerator.get_benchmark_definitions_url(page_indices['next'])

    pagination['pages'] = []
    for index in page_indices['page_indices']:
        pag = {}
        pag['index'] = index
        pag['url'] = ViewUrlGenerator.get_benchmark_definitions_url(index)
        pag['is_current'] = (index == page_indices['current'])
        pagination['pages'].append(pag)
    return pagination

def prepare_pagination_bench_stacked(project_entry, branch_entry, bench_def_entry, worker_entry, page_indices):
    """ Creates pagination object for workers from indices """
    pagination = {}
    pagination['prev'] = ViewUrlGenerator.get_benchmark_execution_stacked_url(
        project_entry,
        branch_entry,
        bench_def_entry,
        worker_entry,
        page_indices['prev'])

    pagination['current'] = ViewUrlGenerator.get_benchmark_execution_stacked_url(
        project_entry,
        branch_entry,
        bench_def_entry,
        worker_entry,
        page_indices['current'])

    pagination['next'] = ViewUrlGenerator.get_benchmark_execution_stacked_url(
        project_entry,
        branch_entry,
        bench_def_entry,
        worker_entry,
        page_indices['next'])

    pagination['pages'] = []
    for index in page_indices['page_indices']:
        pag = {}
        pag['index'] = index
        pag['url'] = ViewUrlGenerator.get_benchmark_execution_stacked_url(
            project_entry,
            branch_entry,
            bench_def_entry,
            worker_entry,
            index)
        pag['is_current'] = (index == page_indices['current'])
        pagination['pages'].append(pag)
    return pagination

def prepare_project_for_html(project):
    """ Adds information to project objects for template interaction """
    project['url'] = {}
    project['url']['save'] = ViewUrlGenerator.get_save_project_url(project['id'])
    project['url']['delete'] = ViewUrlGenerator.get_delete_project_url(project['id'])
    project['url']['edit'] = ViewUrlGenerator.get_project_edit_url(project['id'])
    return project

def prepare_menu_for_html(menu):
    """ Adds default items to menu plus already existing ones """
    menu_items = []

    item_1 = {}
    item_1['name'] = ''
    item_1['icon'] = 'fa fa-home fa-lg'
    item_1['link'] = '/main/view/'

    item_2 = {}
    item_2['name'] = 'Layouts'
    item_2['icon'] = ''
    item_2['link'] = ViewUrlGenerator.get_layout_all_url(1)

    item_3 = {}
    item_3['name'] = 'Projects'
    item_3['icon'] = ''
    item_3['link'] = ViewUrlGenerator.get_project_all_url(1)

    item_4 = {}
    item_4['name'] = 'Workers'
    item_4['icon'] = ''
    item_4['link'] = ViewUrlGenerator.get_worker_all_url(1)

    item_5 = {}
    item_5['name'] = 'Definitions'
    item_5['icon'] = ''
    item_5['link'] = ViewUrlGenerator.get_benchmark_definitions_url(1)

    item_6 = {}
    item_6['name'] = 'Executions'
    item_6['icon'] = ''
    item_6['link'] = ViewUrlGenerator.get_benchmark_executions_quick_url()

    menu_items.append(item_1)
    menu_items.append(item_2)
    menu_items.append(item_3)
    menu_items.append(item_4)
    menu_items.append(item_5)
    menu_items.append(item_6)

    for item in menu:
        menu_items.append(item)

    return menu_items


def prepare_workers_for_html(workers):
    """ Prepares workers for html template """
    worker_items = []

    for worker in workers:
        worker['url'] = {}
        worker['url']['single'] = ViewUrlGenerator.get_worker_url(worker['id'])
        worker['url']['feed_report'] = ViewUrlGenerator.get_feed_report_form_worker_url(worker['id'], 1)
        worker['url']['edit'] = ViewUrlGenerator.get_worker_edit_url(worker['id'])
        worker['icon'] = 'fa-question-circle'

        if any(x in worker['operative_system'].lower() for x in ['win', 'windows']):
            worker['icon'] = 'fa-windows'

        if any(x in worker['operative_system'].lower() for x in ['darwin', 'osx']):
            worker['icon'] = 'fa-apple'

        if any(x in worker['operative_system'].lower() for x in ['linux']):
            worker['icon'] = 'fa-linux'

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
        for commit in branch['commits']:
            commit['url'] = {}
            commit['url']['executions'] = ViewUrlGenerator.get_commit_ordered_by_worker_url(commit['id'])

        branch['url'] = {}
        branch['url']['single'] = ViewUrlGenerator.get_project_branch_single_url(project_id, branch['id'])
        branch['url']['links'] = ViewUrlGenerator.get_project_branch_single_links_url(project_id, branch['id'])
        ret_branches.append(branch)
    return ret_branches

def prepare_benchmark_execution_for_html(execution, domain):
    """ Parepares an execution object to json, ie: serializing date times :D """
    obj = execution
    obj['url'] = {}
    obj['url']['save'] = ViewUrlGenerator.get_save_bench_exe_full_url(domain, obj['id'])

    for command in execution['definition']['command_set']['commands']:
        command['command'] = command['command'].replace('{commit_hash}', execution['commit'])

    return obj

def prepare_results_from_bench_exec_to_html(execution):
    """ Extract results from a benchmark execution """
    results = []

    for index, command in enumerate(execution['report']['commands']):

        com = {}
        com['command'] = command['command']
        com['status'] = command['result'].get('status', 0)
        com['error'] = command['result'].get('error', '')
        com['out'] = []

        out_json = []

        try:
            out_json = json.loads(command['result'].get('out', '[]'))
        except ValueError as error:
            res = {}
            res['id'] = 'error-{0}'.format(index)
            res['visual_type'] = 'unknown'
            res['data'] = '{0}\n{1}'.format(
                str(error),
                command['result']['out'])
            out_json.append(res)
        except KeyError as error:
            res = {}
            res['id'] = 'error-{0}'.format(index)
            res['visual_type'] = 'unknown'
            res['data'] = '{0}\n{1}'.format(
                str(error),
                command['result']['out'])
            out_json.append(res)

        for ent in out_json:
            tmp = {}
            tmp['obj'] = ent
            tmp['json'] = json.dumps(ent)
            com['out'].append(tmp)

        results.append(com)

    return results

def prepare_stacked_executions_url_field(domain, executions):
    """ Prepare stacked execitions of html """
    results = []
    for key in executions:
        item = {}
        item['id'] = key
        item['data'] = executions[key]

        for bench_data in item['data']:
            bench_data['benchmark_execution_url'] = ViewUrlGenerator.get_benchmark_execution_relevant_full_url(
                domain,
                bench_data['benchmark_execution_id'])

        results.append(item)

    return results

def prepare_stacked_executions_json_field(executions):
    """ Prepare stacked execitions of html """
    for item in executions:
        item['json'] = json.dumps(item['data'])
    return executions

def prepare_windowed_executions_colors(executions, center_commit_hash):
    """
    This function will mark all the commit executions to be from other branch except for the passed commit.
    This is because we want to emphatize the centered commit.
    """
    for item in executions:
        for execution in item['data']:
            if center_commit_hash.startswith(execution['benchmark_execution_hash']):
                execution['bar_type'] = 'current_branch'
            else:
                execution['bar_type'] = 'other_branch'

    return executions
