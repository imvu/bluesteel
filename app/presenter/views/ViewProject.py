""" Presenter views, Project page functions """

from app.presenter.views import ViewUrlGenerator
from app.service.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.service.bluesteel.controllers.BluesteelProjectController import BluesteelProjectController
from app.service.bluesteel.managers.BluesteelLayoutManager import BluesteelLayoutManager
from app.service.bluesteel.views import BluesteelSchemas
from app.util.commandrepo.models.CommandGroupModel import CommandGroupEntry
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

        CommandGroupEntry.objects.delete_command_group_by_id(project_entry.command_group.id)

        project_entry.name = val_resp_obj['name']
        project_entry.command_group = CommandGroupEntry.objects.create()
        project_entry.save()

        CommandGroupEntry.objects.add_full_command_set(project_entry.command_group, 'CLONE', 0, val_resp_obj['clone'])
        CommandGroupEntry.objects.add_full_command_set(project_entry.command_group, 'FETCH', 1, val_resp_obj['fetch'])
        CommandGroupEntry.objects.add_full_command_set(project_entry.command_group, 'PULL', 2, val_resp_obj['pull'])

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
        BluesteelLayoutManager.sort_layout_projects_by_order(project_entry.layout)

        obj = {}
        obj['redirect'] = ViewUrlGenerator.get_layout_edit_url(layout_id)
        return res.get_response(200, 'Project deleted', obj)
    else:
        return res.get_only_post_allowed({})

def get_project_branches(request, project_id):
    """ Display all the branches of a project """
    if request.method == 'GET':
        project_entry = BluesteelProjectEntry.objects.filter(id=project_id).first()
        if project_entry == None:
            return res.get_template_data(request, 'presenter/not_found.html', {})

        data = {}
        data['branches'] = BluesteelProjectController.get_project_git_branch_data(project_entry)

        return res.get_template_data(request, 'presenter/project_branches.html', data)
    else:
        return res.get_template_data(request, 'presenter/not_found.html', {})
