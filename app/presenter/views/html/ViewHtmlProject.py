""" Presenter views, Project page functions """

from app.presenter.views.helpers import ViewUrlGenerator
from app.presenter.views.helpers import ViewPrepareObjects
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.logic.bluesteel.controllers.BluesteelProjectController import BluesteelProjectController
from app.logic.benchmark.controllers.BenchmarkExecutionController import BenchmarkExecutionController
from app.logic.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.logic.bluesteelworker.models.WorkerModel import WorkerEntry
from app.logic.gitrepo.models.GitBranchModel import GitBranchEntry
from app.logic.httpcommon import res
from app.logic.httpcommon.Page import Page

PROJECTS_ITEMS_PER_PAGE = 6
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
            obj['url'] = ViewUrlGenerator.get_project_branches_url(project['id'], BRANCH_COMMIT_DEPTH, 1)
            items.append(obj)

        pagination = ViewPrepareObjects.prepare_pagination_project(page_indices)

        data = {}
        data['items'] = items
        data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])
        data['pagination'] = pagination

        return res.get_template_data(request, 'presenter/single_item_list.html', data)
    else:
        return res.get_template_data(request, 'presenter/not_found.html', {})

def get_project_branches(request, project_id, commit_depth, page_index):
    """ Display all the branches of a project """
    if request.method == 'GET':
        project_entry = BluesteelProjectEntry.objects.filter(id=project_id).first()
        if project_entry == None:
            return res.get_template_data(request, 'presenter/not_found.html', {})

        page = Page(PROJECTS_ITEMS_PER_PAGE, page_index)
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
        if project_entry == None:
            return res.get_template_data(request, 'presenter/not_found.html', {})

        branch_entry = GitBranchEntry.objects.filter(id=branch_id, project=project_entry.git_project.id).first()
        if branch_entry == None:
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
        branch_entry = GitBranchEntry.objects.filter(id=branch_id, project__id=project_id).first()
        if branch_entry == None:
            return res.get_template_data(request, 'presenter/not_found.html', {})

        def_entries = BenchmarkDefinitionEntry.objects.all()
        worker_entries = WorkerEntry.objects.all()

        # project_entry, branch_entry, bench_def_entry, worker_entry

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

        data = {}
        data['branch'] = {}
        data['branch']['name'] = branch_entry.name
        data['branch']['url'] = {}
        data['branch']['url']['single'] = ViewUrlGenerator.get_project_branch_single_url(project_id, branch_id)
        data['branch']['links'] = links
        data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])

        return res.get_template_data(request, 'presenter/project_branch_links.html', data)
    else:
        return res.get_template_data(request, 'presenter/not_found.html', {})
