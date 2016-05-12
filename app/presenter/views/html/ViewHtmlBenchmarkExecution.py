""" Presenter views, benchmark execution page functions """

from app.presenter.views.helpers import ViewPrepareObjects
from app.presenter.views.helpers import ViewUrlGenerator
from app.logic.benchmark.controllers.BenchmarkExecutionController import BenchmarkExecutionController
from app.logic.benchmark.models.BenchmarkExecutionModel import BenchmarkExecutionEntry
from app.logic.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.logic.gitrepo.controllers.GitController import GitController
from app.logic.gitrepo.models.GitBranchModel import GitBranchEntry
from app.logic.bluesteelworker.models.WorkerModel import WorkerEntry
from app.logic.httpcommon import res
from app.logic.httpcommon.Page import Page

BENCH_EXEC_ITEMS_PER_PAGE = 25
BENCH_EXEC_WINDOW_HALF = 4

def get_benchmark_execution_relevant(request, bench_exec_id):
    """ Returns a benchmark execution """
    data = {}
    data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])

    exec_entry = BenchmarkExecutionEntry.objects.filter(id=bench_exec_id).first()

    if exec_entry == None:
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

    if exec_entry == None:
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

        commits_hashes = GitController.get_commit_hashes_parents_and_children(
            project=bench_exec.definition.project,
            commit_hash=bench_exec.commit.commit_hash,
            parents_children_count=BENCH_EXEC_WINDOW_HALF
        )

        branch_name = GitController.get_best_branch_from_a_commit(
            project_entry=bench_exec.definition.project,
            commit_hash=bench_exec.commit.commit_hash
        )

        branch = GitBranchEntry.objects.filter(project=bench_exec.definition.project, name=branch_name).first()

        if not branch:
            return res.get_template_data(request, 'presenter/not_found.html', {})

        commits_hashes = list(reversed(commits_hashes))

        data = BenchmarkExecutionController.get_stacked_executions_from_branch(
            bench_exec.definition.project,
            branch,
            commits_hashes,
            bench_exec.definition,
            bench_exec.worker
        )

        executions = BenchmarkExecutionController.get_stacked_data_separated_by_id(data)
        executions = ViewPrepareObjects.prepare_stacked_executions_for_html(request.get_host(), executions)

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
        if project == None:
            return res.get_template_data(request, 'presenter/not_found.html', {})

        branch = GitBranchEntry.objects.filter(id=branch_id, project=project.git_project.id).first()
        if branch == None:
            return res.get_template_data(request, 'presenter/not_found.html', {})

        definition = BenchmarkDefinitionEntry.objects.filter(id=definition_id, project=project).first()
        if definition == None:
            return res.get_template_data(request, 'presenter/not_found.html', {})

        worker = WorkerEntry.objects.filter(id=worker_id).first()
        if worker == None:
            return res.get_template_data(request, 'presenter/not_found.html', {})

        page = Page(BENCH_EXEC_ITEMS_PER_PAGE, page_index)
        commit_hashes, pagination = BenchmarkExecutionController.get_bench_exec_commits_paginated(
            project,
            branch,
            page
        )

        pagination = ViewPrepareObjects.prepare_pagination_bench_stacked(
            project_id,
            branch_id,
            definition_id,
            worker_id,
            pagination)

        data = BenchmarkExecutionController.get_stacked_executions_from_branch(
            project,
            branch,
            commit_hashes,
            definition,
            worker
        )

        executions = BenchmarkExecutionController.get_stacked_data_separated_by_id(data)

        executions = ViewPrepareObjects.prepare_stacked_executions_for_html(request.get_host(), executions)

        data = {}
        data['stacked_executions'] = executions
        data['pagination'] = pagination
        data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])

        return res.get_template_data(request, 'presenter/benchmark_execution_stacked.html', data)
    else:
        return res.get_template_data(request, 'presenter/not_found.html', {})
