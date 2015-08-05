""" Presenter views, Project page functions """

from app.service.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.service.bluesteel.views import BluesteelSchemas
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



    else:
        return res.get_only_post_allowed({})
