""" Presenter views, Project page functions """

from app.service.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.service.bluesteel.views import BluesteelSchemas
from app.util.commandrepo.models.CommandGroupModel import CommandGroupEntry
from app.util.httpcommon import res
from app.util.httpcommon import val

def save_project(request, project_id):
    """ Returns html for the layout editable page """
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
