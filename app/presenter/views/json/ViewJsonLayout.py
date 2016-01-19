""" Presenter json views, layout page functions """

from app.presenter.views.helpers import ViewUrlGenerator
from app.presenter.schemas import BluesteelSchemas
from app.logic.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.logic.bluesteel.controllers.BluesteelLayoutController import BluesteelLayoutController
from app.logic.httpcommon import res
from app.logic.httpcommon import val

def post_create_new_layout(request):
    """ Create a new layout and return the ID of it """
    if request.method == 'POST':
        new_layout = BluesteelLayoutController.create_new_default_layout()

        data = {}
        # data['layout'] = new_layout.as_object()
        # data['layout'] = ViewPrepareObjects.prepare_layout_for_html(data['layout'])
        data['redirect'] = ViewUrlGenerator.get_layout_edit_url(new_layout.id)

        return res.get_response(200, 'New layout created', data)
    else:
        return res.get_only_post_allowed({})

def delete(request, layout_id):
    """ Layout deletion """
    if request.method == 'POST':
        layout_entry = BluesteelLayoutEntry.objects.filter(id=layout_id).first()
        if layout_entry == None:
            return res.get_response(404, 'Bluesteel layout not found', {})

        BluesteelLayoutController.delete_layout(layout_entry)

        data = {}
        data['redirect'] = ViewUrlGenerator.get_layout_all_url()
        return res.get_response(200, 'Layout deleted', data)
    else:
        return res.get_only_post_allowed({})

def save_layout(request, layout_id):
    """ Save layout properties """
    if request.method == 'POST':
        layout_entry = BluesteelLayoutEntry.objects.filter(id=layout_id).first()
        if layout_entry == None:
            return res.get_response(404, 'Bluesteel layout not found', {})

        (json_valid, post_info) = val.validate_json_string(request.body)
        if not json_valid:
            return res.get_json_parser_failed({})

        (obj_validated, val_resp_obj) = val.validate_obj_schema(post_info, BluesteelSchemas.SAVE_LAYOUT)

        if not obj_validated:
            return res.get_schema_failed(val_resp_obj)

        layout_entry.name = val_resp_obj['name']
        layout_entry.active = val_resp_obj['active']
        layout_entry.project_index_path = val_resp_obj['project_index_path']
        # Check if change of path in case we need to purge other services like 'performance tests service'
        layout_entry.clamp_project_index_path()
        layout_entry.check_active_state()
        layout_entry.save()
        return res.get_response(200, 'Layout saved', {})
    else:
        return res.get_only_post_allowed({})

def add_default_project(request, layout_id):
    """ Add default projet to layout """
    if request.method == 'POST':
        layout_entry = BluesteelLayoutEntry.objects.filter(id=layout_id).first()
        if layout_entry == None:
            return res.get_response(404, 'Bluesteel layout not found', {})

        BluesteelLayoutController.add_default_project_to_layout(layout_entry)
        BluesteelLayoutController.sort_layout_projects_by_order(layout_entry)

        obj = {}
        obj['redirect'] = ViewUrlGenerator.get_layout_edit_url(layout_entry.id)
        return res.get_response(200, 'Layout saved!', obj)
    else:
        return res.get_only_post_allowed({})
