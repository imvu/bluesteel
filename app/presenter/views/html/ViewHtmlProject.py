""" Presenter views, Project page functions """

from app.presenter.views.helpers import ViewUrlGenerator
from app.presenter.views.helpers import ViewPrepareObjects
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.logic.bluesteel.controllers.BluesteelProjectController import BluesteelProjectController
from app.logic.benchmark.controllers.BenchmarkExecutionController import BenchmarkExecutionController
from app.logic.gitrepo.models.GitBranchModel import GitBranchEntry
from app.logic.httpcommon import res

def get_projects(request):
    """ Display all branch names """
    if request.method == 'GET':
        project_entries = BluesteelProjectEntry.objects.all()

        items = []
        for project in project_entries:
            obj = {}
            obj['name'] = project.name
            obj['url'] = ViewUrlGenerator.get_project_branches_url(project.id)
            items.append(obj)

        data = {}
        data['items'] = items
        data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])

        return res.get_template_data(request, 'presenter/single_item_list.html', data)
    else:
        return res.get_template_data(request, 'presenter/not_found.html', {})

def get_project_branches(request, project_id):
    """ Display all the branches of a project """
    if request.method == 'GET':
        project_entry = BluesteelProjectEntry.objects.filter(id=project_id).first()
        if project_entry == None:
            return res.get_template_data(request, 'presenter/not_found.html', {})

        branches = BluesteelProjectController.get_project_git_branch_data(project_entry)
        branches = BenchmarkExecutionController.add_bench_exec_completed_to_branches(branches)

        data = {}
        data['branches'] = ViewPrepareObjects.prepare_branches_for_html(project_entry.id, branches)
        data['url'] = {}
        data['url']['change_merge_target'] = ViewUrlGenerator.get_change_merge_target_url(project_entry.id)
        data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])

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

        branches = BluesteelProjectController.get_project_single_git_branch_data(project_entry, branch_entry)
        branches = BenchmarkExecutionController.add_bench_exec_completed_to_branches(branches)

        data = {}
        data['branches'] = ViewPrepareObjects.prepare_branches_for_html(project_entry.id, branches)
        data['url'] = {}
        data['url']['change_merge_target'] = ViewUrlGenerator.get_change_merge_target_url(project_entry.id)
        data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])

        return res.get_template_data(request, 'presenter/project_branches.html', data)
    else:
        return res.get_template_data(request, 'presenter/not_found.html', {})
