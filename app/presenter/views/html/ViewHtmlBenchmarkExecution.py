""" Presenter views, benchmark execution page functions """

from app.presenter.views.helpers import ViewPrepareObjects
from app.presenter.views.helpers import ViewUrlGenerator
from app.logic.benchmark.controllers.BenchmarkExecutionController import BenchmarkExecutionController
from app.logic.benchmark.models.BenchmarkExecutionModel import BenchmarkExecutionEntry
from app.logic.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.logic.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.logic.gitrepo.controllers.GitController import GitController
from app.logic.gitrepo.models.GitProjectModel import GitProjectEntry
from app.logic.gitrepo.models.GitBranchModel import GitBranchEntry
from app.logic.bluesteelworker.models.WorkerModel import WorkerEntry
from app.logic.httpcommon import res
from app.logic.httpcommon.Page import Page

BENCH_EXEC_ITEMS_PER_PAGE = 25
BENCH_EXEC_WINDOW_HALF = 4

def get_benchmark_executions_of_branch(request):
    if request.method == 'GET':
        layouts_obj = []
        layouts = BluesteelLayoutEntry.objects.all()

        for layout in layouts:
            layout_obj = {}
            layout_obj['id'] = layout.id
            layout_obj['name'] = layout.name
            layout_obj['projects'] = []

            projects = BluesteelProjectEntry.objects.filter(layout__id=layout.id)

            for project in projects:
                git_project = GitProjectEntry.objects.filter(id=project.git_project.id).first()

                if git_project is None:
                    continue

                branch_names_and_orders = GitController.get_branch_names_and_order_values(git_project)
                executions_branch = []
                for name_and_order in branch_names_and_orders:
                    obj = {}
                    obj['name'] = name_and_order['name']
                    obj['order'] = name_and_order['order']
                    obj['url'] = {}
                    obj['url']['executions_branch'] = ViewUrlGenerator.get_project_branch_single_links_url(
                        git_project.id,
                        name_and_order['id'])
                    executions_branch.append(obj)

                project_obj = {}
                project_obj['name'] = project.name
                project_obj['git_project_id'] = git_project.id
                project_obj['branches'] = executions_branch
                layout_obj['projects'].append(project_obj)

            layouts_obj.append(layout_obj)


        data = {}
        data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])
        data['layouts'] = layouts_obj

        return res.get_template_data(request, 'presenter/benchmark_executions_branches.html', data)
    else:
        return res.get_template_data(request, 'presenter/not_found.html', {})

def get_benchmark_execution_relevant(request, bench_exec_id):
    """ Returns a benchmark execution """
    data = {}
    data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])

    exec_entry = BenchmarkExecutionEntry.objects.filter(id=bench_exec_id).first()

    if exec_entry is None:
        return res.get_template_data(request, 'presenter/not_found.html', data)

    obj = exec_entry.as_object()
    data['results'] = ViewPrepareObjects.prepare_results_from_bench_exec_to_html(obj)
    data['url'] = {}
    data['url']['invalidate'] = ViewUrlGenerator.get_benchmark_execution_invalidate_url(exec_entry.id)
    data['url']['complete'] = ViewUrlGenerator.get_benchmark_execution_complete_url(exec_entry.id)

    return res.get_template_data(request, 'presenter/benchmark_execution_relevant.html', data)

def get_benchmark_execution_complete(request, bench_exec_id):
    """ Returns a benchmark execution """
    data = {}
    data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])

    exec_entry = BenchmarkExecutionEntry.objects.filter(id=bench_exec_id).first()

    if exec_entry is None:
        return res.get_template_data(request, 'presenter/not_found.html', data)

    obj = exec_entry.as_object()
    data['results'] = ViewPrepareObjects.prepare_results_from_bench_exec_to_html(obj)
    data['url'] = {}
    data['url']['invalidate'] = ViewUrlGenerator.get_benchmark_execution_invalidate_url(exec_entry.id)
    data['url']['relevant'] = ViewUrlGenerator.get_benchmark_execution_relevant_url(exec_entry.id)

    return res.get_template_data(request, 'presenter/benchmark_execution_complete.html', data)

def get_benchmark_execution_window(request, bench_exec_id):
    """ Returns a window of benchmark executions centered on bench_exe_id """
    if request.method == 'GET':
        bench_exec = BenchmarkExecutionEntry.objects.filter(id=bench_exec_id).first()
        if not bench_exec:
            return res.get_template_data(request, 'presenter/not_found.html', {})

        commit_hash = bench_exec.commit.commit_hash

        exec_stacked = BenchmarkExecutionController.get_benchmark_execution_window(bench_exec, BENCH_EXEC_WINDOW_HALF)
        executions = ViewPrepareObjects.prepare_stacked_executions_for_html(request.get_host(), exec_stacked)
        executions = ViewPrepareObjects.prepare_windowed_executions_colors(executions, commit_hash)
        executions = ViewPrepareObjects.prepare_stacked_executions_json_field(executions)

        data = {}
        data['stacked_executions'] = executions
        data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])

        return res.get_template_data(request, 'presenter/benchmark_execution_stacked.html', data)
    else:
        return res.get_template_data(request, 'presenter/not_found.html', {})

def get_benchmark_executions_stacked(request, project_id, branch_id, definition_id, worker_id, page_index):
    """ Returns benchmark executions stacked and paginated """
    if request.method == 'GET':
        project = BluesteelProjectEntry.objects.filter(id=project_id).first()
        if project is None:
            return res.get_template_data(request, 'presenter/not_found.html', {})

        git_project = GitProjectEntry.objects.filter(id=project.git_project.id).first()
        if git_project is None:
            return res.get_template_data(request, 'presenter/not_found.html', {})

        branch = GitBranchEntry.objects.filter(id=branch_id, project=git_project).first()
        if branch is None:
            return res.get_template_data(request, 'presenter/not_found.html', {})

        definition = BenchmarkDefinitionEntry.objects.filter(id=definition_id, project=project).first()
        if definition is None:
            return res.get_template_data(request, 'presenter/not_found.html', {})

        worker = WorkerEntry.objects.filter(id=worker_id).first()
        if worker is None:
            return res.get_template_data(request, 'presenter/not_found.html', {})

        page = Page(BENCH_EXEC_ITEMS_PER_PAGE, page_index)
        commit_hashes, pagination = BenchmarkExecutionController.get_bench_exec_commits_paginated(
            git_project,
            branch,
            page
        )

        pagination = ViewPrepareObjects.prepare_pagination_bench_stacked(
            project_id,
            branch_id,
            definition_id,
            worker_id,
            pagination)

        data_exec = BenchmarkExecutionController.get_stacked_executions_from_branch(
            git_project,
            branch,
            commit_hashes,
            definition,
            worker
        )

        exec_stacked = BenchmarkExecutionController.get_stacked_data_separated_by_id(data_exec)

        executions = ViewPrepareObjects.prepare_stacked_executions_for_html(request.get_host(), exec_stacked)
        executions = ViewPrepareObjects.prepare_stacked_executions_json_field(executions)

        data = {}
        data['stacked_executions'] = executions
        data['pagination'] = pagination
        data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])

        return res.get_template_data(request, 'presenter/benchmark_execution_stacked.html', data)
    else:
        return res.get_template_data(request, 'presenter/not_found.html', {})
