""" Presenter views, Project page functions """

from app.presenter.views import ViewUrlGenerator
from app.presenter.views import ViewPrepareObjects
from app.service.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.service.bluesteel.controllers.BluesteelProjectController import BluesteelProjectController
from app.service.bluesteel.controllers.BluesteelLayoutController import BluesteelLayoutController
from app.service.bluesteel.views import BluesteelSchemas
from app.service.gitrepo.models.GitBranchModel import GitBranchEntry
from app.util.commandrepo.models.CommandGroupModel import CommandGroupEntry
from app.util.commandrepo.controllers.CommandController import CommandController
from app.util.httpcommon import res
from app.util.httpcommon import val

def save_project(request, project_id):
    """ Save project properties """
    if request.method == 'POST':
        project_entry = BluesteelProjectEntry.objects.filter(id=project_id).first()
        if project_entry == None:
            return res.get_response(404, 'Bluesteel project not found', {})

        (json_valid, post_info) = val.validate_json_string(request.body)
        if not json_valid:
            return res.get_json_parser_failed({})

        (obj_validated, val_resp_obj) = val.validate_obj_schema(post_info, BluesteelSchemas.SAVE_PROJECT)

        if not obj_validated:
            return res.get_schema_failed(val_resp_obj)

        CommandController.delete_command_group_by_id(project_entry.command_group.id)

        project_entry.name = val_resp_obj['name']
        project_entry.command_group = CommandGroupEntry.objects.create()
        project_entry.save()

        CommandController.add_full_command_set(project_entry.command_group, 'CLONE', 0, val_resp_obj['clone'])
        CommandController.add_full_command_set(project_entry.command_group, 'FETCH', 1, val_resp_obj['fetch'])
        CommandController.add_full_command_set(project_entry.command_group, 'PULL', 2, val_resp_obj['pull'])

        return res.get_response(200, 'Project saved', {})
    else:
        return res.get_only_post_allowed({})

def delete_project(request, project_id):
    """ Delete project on a layout """
    if request.method == 'POST':
        project_entry = BluesteelProjectEntry.objects.filter(id=project_id).first()
        if project_entry == None:
            return res.get_response(404, 'Bluesteel project not found', {})

        layout_id = project_entry.layout.id
        project_entry.layout.active = False
        project_entry.layout.save()

        BluesteelProjectController.delete_project(project_entry)
        BluesteelLayoutController.sort_layout_projects_by_order(project_entry.layout)

        obj = {}
        obj['redirect'] = ViewUrlGenerator.get_layout_edit_url(layout_id)
        return res.get_response(200, 'Project deleted', obj)
    else:
        return res.get_only_post_allowed({})

def get_projects(request):
    """ Display all branch names """
    if request.method == 'GET':
        project_entries = BluesteelProjectEntry.objects.all()

        projects = []
        for project in project_entries:
            print project.as_object()

            obj = {}
            obj['name'] = project.name
            obj['url'] = {}
            obj['url']['branches'] = ViewUrlGenerator.get_project_branches_url(project.id)
            projects.append(obj)

        data = {}
        data['projects'] = projects
        data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])

        print data

        return res.get_template_data(request, 'presenter/projects.html', data)
    else:
        return res.get_template_data(request, 'presenter/not_found.html', {})

def get_project_branches(request, project_id):
    """ Display all the branches of a project """
    if request.method == 'GET':
        project_entry = BluesteelProjectEntry.objects.filter(id=project_id).first()
        if project_entry == None:
            return res.get_template_data(request, 'presenter/not_found.html', {})

        branches = BluesteelProjectController.get_project_git_branch_data(project_entry)

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

        data = {}
        data['branches'] = ViewPrepareObjects.prepare_branches_for_html(project_entry.id, branches)
        data['url'] = {}
        data['url']['change_merge_target'] = ViewUrlGenerator.get_change_merge_target_url(project_entry.id)
        data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])

        return res.get_template_data(request, 'presenter/project_branches.html', data)
    else:
        return res.get_template_data(request, 'presenter/not_found.html', {})
