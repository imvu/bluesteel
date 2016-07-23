""" Presenter views, Project page functions """

from app.presenter.views.helpers import ViewUrlGenerator
from app.presenter.views.helpers import ViewPrepareObjects
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.logic.bluesteel.controllers.BluesteelProjectController import BluesteelProjectController
from app.logic.benchmark.controllers.BenchmarkExecutionController import BenchmarkExecutionController
from app.logic.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.logic.bluesteelworker.models.WorkerModel import WorkerEntry
from app.logic.gitrepo.controllers.GitController import GitController
from app.logic.gitrepo.models.GitProjectModel import GitProjectEntry
from app.logic.gitrepo.models.GitBranchModel import GitBranchEntry
from app.logic.httpcommon import res
from app.logic.httpcommon.Page import Page

PROJECTS_ITEMS_PER_PAGE = 6
PROJECTS_BRANCHES_PER_PAGE = 4
BRANCH_COMMIT_DEPTH = 100

def get_projects(request, page_index):
    """ Display all branch names """
    if request.method == 'GET':
        page = Page(PROJECTS_ITEMS_PER_PAGE, page_index)
        projects, page_indices = BluesteelProjectController.get_paginated_projects_as_objects(page)

        items = []
        for project in projects:
            obj = {}
            obj['name'] = project['name']
            obj['url'] = {}
            obj['url']['branches'] = ViewUrlGenerator.get_project_branches_url(project['id'], BRANCH_COMMIT_DEPTH, 1)
            obj['url']['edit'] = ViewUrlGenerator.get_project_edit_url(project['id'])
            items.append(obj)

        pagination = ViewPrepareObjects.prepare_pagination_project(page_indices)

        data = {}
        data['projects'] = items
        data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])
        data['pagination'] = pagination

        return res.get_template_data(request, 'presenter/project_list.html', data)
    else:
        return res.get_template_data(request, 'presenter/not_found.html', {})

def get_project_editable(request, project_id):
    """ Returns html for the project editable page """
    if request.method == 'GET':
        project = BluesteelProjectEntry.objects.filter(id=project_id).first()

        if project is None:
            return res.get_template_data(request, 'presenter/not_found.html', {})

        data = {}
        data['project'] = project.as_object()
        data['project'] = ViewPrepareObjects.prepare_project_for_html(data['project'])
        data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])

        return res.get_template_data(request, 'presenter/project_edit.html', data)
    else:
        return res.get_template_data(request, 'presenter/not_found.html', {})

def get_project_branches(request, project_id, commit_depth, page_index):
    """ Display all the branches of a project """
    if request.method == 'GET':
        project_entry = BluesteelProjectEntry.objects.filter(id=project_id).first()
        if project_entry is None:
            return res.get_template_data(request, 'presenter/not_found.html', {})

        page = Page(PROJECTS_BRANCHES_PER_PAGE, page_index)
        branches, page_indices = BluesteelProjectController.get_project_git_branch_data(
            page,
            project_entry,
            commit_depth
        )
        branches = BenchmarkExecutionController.add_bench_exec_completed_to_branches(branches)

        pagination = ViewPrepareObjects.prepare_pagination_branches(project_entry.id, commit_depth, page_indices)

        data = {}
        data['branches'] = ViewPrepareObjects.prepare_branches_for_html(project_entry.id, branches)
        data['url'] = {}
        data['url']['change_merge_target'] = ViewUrlGenerator.get_change_merge_target_url(project_entry.id)
        data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])
        data['pagination'] = pagination

        return res.get_template_data(request, 'presenter/project_branches.html', data)
    else:
        return res.get_template_data(request, 'presenter/not_found.html', {})

def get_project_single_branch(request, project_id, branch_id):
    """ Display all the branches of a project """
    if request.method == 'GET':
        project_entry = BluesteelProjectEntry.objects.filter(id=project_id).first()
        if project_entry is None:
            return res.get_template_data(request, 'presenter/not_found.html', {})

        branch_entry = GitBranchEntry.objects.filter(id=branch_id, project=project_entry.git_project.id).first()
        if branch_entry is None:
            return res.get_template_data(request, 'presenter/not_found.html', {})

        branches = BluesteelProjectController.get_project_single_git_branch_data(
            project_entry,
            branch_entry,
            BRANCH_COMMIT_DEPTH
        )
        branches = BenchmarkExecutionController.add_bench_exec_completed_to_branches(branches)

        data = {}
        data['branches'] = ViewPrepareObjects.prepare_branches_for_html(project_entry.id, branches)
        data['url'] = {}
        data['url']['change_merge_target'] = ViewUrlGenerator.get_change_merge_target_url(project_entry.id)
        data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])

        return res.get_template_data(request, 'presenter/project_branches.html', data)
    else:
        return res.get_template_data(request, 'presenter/not_found.html', {})


def get_project_single_branch_links(request, project_id, branch_id):
    """ Display single branch links """
    if request.method == 'GET':
        project_entry = GitProjectEntry.objects.filter(id=project_id).first()
        if project_entry is None:
            return res.get_template_data(request, 'presenter/not_found.html', {})

        branch_entry = GitBranchEntry.objects.filter(id=branch_id, project=project_entry).first()
        if branch_entry is None:
            return res.get_template_data(request, 'presenter/not_found.html', {})

        def_entries = BenchmarkDefinitionEntry.objects.all()
        worker_entries = WorkerEntry.objects.all()

        links = []

        for def_entry in def_entries:
            definition = {}
            definition['name'] = def_entry.name
            definition['id'] = def_entry.id
            definition['workers'] = []

            for worker_entry in worker_entries:
                worker = {}
                worker['name'] = worker_entry.name
                worker['uuid'] = worker_entry.uuid
                worker['stacked_benchmarks'] = ViewUrlGenerator.get_benchmark_execution_stacked_url(
                    project_id,
                    branch_id,
                    def_entry.id,
                    worker_entry.id,
                    1
                )
                definition['workers'].append(worker)

            links.append(definition)


        branch_names_and_orders = GitController.get_branch_names_and_order_values(project_entry)
        update_order_selection = []
        for name_and_order in branch_names_and_orders:
            obj = {}
            obj['name'] = name_and_order['name']
            obj['order'] = name_and_order['order']
            obj['current'] = name_and_order['id'] == branch_entry.id
            obj['url'] = {}
            obj['url']['update'] = ViewUrlGenerator.get_branch_update_order_url(branch_id, project_id, obj['order'])
            update_order_selection.append(obj)


        data = {}
        data['branch'] = {}
        data['branch']['name'] = branch_entry.name
        data['branch']['order'] = branch_entry.order
        data['branch']['url'] = {}
        data['branch']['url']['single'] = ViewUrlGenerator.get_project_branch_single_url(project_id, branch_id)
        data['branch']['links'] = links
        data['branch']['update_order_selection'] = update_order_selection
        data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])

        return res.get_template_data(request, 'presenter/project_branch_links.html', data)
    else:
        return res.get_template_data(request, 'presenter/not_found.html', {})
