""" View URL generator """

def get_main_url():
    return '/main/view/'

def get_layout_all_url():
    return '/main/layout/all/'

def get_layout_full_url(domain, layout_id):
    return 'http://{0}/main/layout/{1}/'.format(domain, layout_id)

def get_layout_point_full_url(domain):
    return 'http://{0}/main/layout/all/urls/'.format(domain)

def get_layout_create_url():
    return '/main/layout/create/'

def get_layout_edit_url(layout_id):
    return '/main/layout/edit/{0}/'.format(layout_id)

def get_save_layout_url(layout_id):
    return '/main/layout/{0}/save/'.format(layout_id)

def get_delete_layout_url(layout_id):
    return '/main/layout/{0}/delete/'.format(layout_id)

def get_confirm_delete_layout_url(layout_id):
    return '/main/layout/{0}/confirm/delete/'.format(layout_id)

def get_add_default_project_url(layout_id):
    return '/main/layout/{0}/add/project/'.format(layout_id)

def get_editable_projects_info_url():
    return '/main/layout/<0>/projects/info/'

def get_save_project_url(project_id):
    return '/main/project/{0}/save/'.format(project_id)

def get_delete_project_url(project_id):
    return '/main/project/{0}/delete/'.format(project_id)

def get_download_worker_url():
    return '/main/bluesteelworker/download/'

def get_worker_report_url(worker_id):
    return '/main/bluesteelworker/{0}/report/'.format(worker_id)

def get_worker_update_activity_full_url(domain, worker_id):
    return 'http://{0}/main/bluesteelworker/{1}/update/activity/'.format(
        domain,
        worker_id
    )

def get_worker_entry_point_full_url(domain):
    return 'http://{0}/main/bluesteelworker/bootstrap/'.format(domain)

def get_worker_info_point_full_url(domain):
    return 'http://{0}/main/bluesteelworker/'.format(domain)

def get_worker_create_point_full_url(domain):
    return 'http://{0}/main/bluesteelworker/create/'.format(domain)

def get_worker_login_point_full_url(domain):
    return 'http://{0}/main/bluesteelworker/login/'.format(domain)

def get_gitfeeder_full_url(domain, project_id):
    return 'http://{0}/main/feed/commit/project/{1}/'.format(domain, project_id)

def get_change_merge_target_url(project_id):
    return '/main/branch/merge/target/project/{0}/'.format(project_id)

def get_project_branches_url(project_id):
    return '/main/project/{0}/branch/all/'.format(project_id)

def get_project_branch_single_url(project_id, branch_id):
    return '/main/project/{0}/branch/{1}/'.format(project_id, branch_id)

def get_benchmark_definitions_url():
    return '/main/definitions/all/'

def get_create_benchmark_definitions_url():
    return '/main/definitions/create/'

def get_edit_benchmark_definition_url(benchmark_definition_id):
    return '/main/definition/{0}/edit/'.format(benchmark_definition_id)

def get_save_benchmark_definition_url(benchmark_definition_id):
    return '/main/definition/{0}/save/'.format(benchmark_definition_id)

