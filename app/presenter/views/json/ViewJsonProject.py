""" Presenter json views, Project page functions """

from app.presenter.views.helpers import ViewUrlGenerator
from app.presenter.schemas import BluesteelSchemas
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.logic.bluesteel.controllers.BluesteelProjectController import BluesteelProjectController
from app.logic.bluesteel.controllers.BluesteelLayoutController import BluesteelLayoutController
from app.logic.commandrepo.models.CommandSetModel import CommandSetEntry
from app.logic.commandrepo.controllers.CommandController import CommandController
from app.logic.httpcommon import res
from app.logic.httpcommon import val

def filter_folder_path(path):
    """ This function will filter out \\..\\ or \\ at the begining. Also if path becomes empty, . will be used """
    local_search_path = path
    local_search_path = local_search_path.replace('\\..\\', '\\')
    local_search_path = local_search_path.replace('/../', '/')
    if local_search_path.startswith('/') or local_search_path.startswith('\\'):
        local_search_path = local_search_path[1:]
    if len(local_search_path) == 0:
        local_search_path = '.'
    return local_search_path


def save_project(request, project_id):
    """ Save project properties """
    if request.method == 'POST':
        project_entry = BluesteelProjectEntry.objects.filter(id=project_id).first()
        if project_entry is None:
            return res.get_response(404, 'Bluesteel project not found', {})

        (json_valid, post_info) = val.validate_json_string(request.body)
        if not json_valid:
            return res.get_json_parser_failed({})

        (obj_validated, val_resp_obj) = val.validate_obj_schema(post_info, BluesteelSchemas.SAVE_PROJECT)

        if not obj_validated:
            return res.get_schema_failed(val_resp_obj)

        CommandSetEntry.objects.filter(group=project_entry.command_group).delete()

        local_search_path = filter_folder_path(val_resp_obj['git_project_folder_search_path'])

        project_entry.name = val_resp_obj['name']
        project_entry.git_project_folder_search_path = local_search_path
        project_entry.save()

        CommandController.add_full_command_set(project_entry.command_group, 'CLONE', 0, val_resp_obj['clone'])
        CommandController.add_full_command_set(project_entry.command_group, 'FETCH', 1, val_resp_obj['fetch'])

        return res.get_response(200, 'Project saved', {})
    else:
        return res.get_only_post_allowed({})

def delete_project(request, project_id):
    """ Delete project on a layout """
    if request.method == 'POST':
        project_entry = BluesteelProjectEntry.objects.filter(id=project_id).first()
        if project_entry is None:
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
