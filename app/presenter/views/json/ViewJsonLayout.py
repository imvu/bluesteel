""" Presenter json views, layout page functions """

from django.db import transaction
from app.presenter.views.helpers import ViewUrlGenerator
from app.presenter.schemas import BluesteelSchemas
from app.logic.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.logic.bluesteel.controllers.BluesteelLayoutController import BluesteelLayoutController
from app.logic.httpcommon import res
from app.logic.httpcommon import val

@transaction.atomic
def post_create_new_layout(request):
    """ Create a new layout and return the ID of it """
    if request.method != 'POST':
        return res.get_only_post_allowed({})

    new_layout = BluesteelLayoutController.create_new_default_layout()

    data = {}
    # data['layout'] = new_layout.as_object()
    # data['layout'] = ViewPrepareObjects.prepare_layout_for_html(data['layout'])
    data['redirect'] = ViewUrlGenerator.get_layout_edit_url(new_layout.id)

    return res.get_response(200, 'New layout created', data)

@transaction.atomic
def delete(request, layout_id):
    """ Layout deletion """
    if request.method != 'POST':
        return res.get_only_post_allowed({})

    layout_entry = BluesteelLayoutEntry.objects.filter(id=layout_id).first()
    if layout_entry is None:
        return res.get_response(404, 'Bluesteel layout not found', {})

    BluesteelLayoutController.delete_layout(layout_entry)

    data = {}
    data['redirect'] = ViewUrlGenerator.get_layout_all_url(1)
    return res.get_response(200, 'Layout deleted', data)


@transaction.atomic
def wipe(request, layout_id):
    """ Layout wipe data """
    if request.method != 'POST':
        return res.get_only_post_allowed({})

    layout_entry = BluesteelLayoutEntry.objects.filter(id=layout_id).first()
    if layout_entry is None:
        return res.get_response(404, 'Bluesteel layout not found', {})

    project_entries = BluesteelProjectEntry.objects.filter(layout=layout_entry)

    for project in project_entries:
        project.wipe_data()

    data = {}
    data['redirect'] = ViewUrlGenerator.get_layout_all_url(1)
    return res.get_response(200, 'Layout wiped', data)

@transaction.atomic
def save_layout(request, layout_id):
    """ Save layout properties """
    if request.method != 'POST':
        return res.get_only_post_allowed({})

    layout_entry = BluesteelLayoutEntry.objects.filter(id=layout_id).first()
    if layout_entry is None:
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


@transaction.atomic
def add_default_project(request, layout_id):
    """ Add default projet to layout """
    if request.method != 'POST':
        return res.get_only_post_allowed({})

    layout_entry = BluesteelLayoutEntry.objects.filter(id=layout_id).first()
    if layout_entry is None:
        return res.get_response(404, 'Bluesteel layout not found', {})

    BluesteelLayoutController.add_default_project_to_layout(layout_entry)
    BluesteelLayoutController.sort_layout_projects_by_order(layout_entry)

    obj = {}
    obj['redirect'] = ViewUrlGenerator.get_layout_edit_url(layout_entry.id)
    return res.get_response(200, 'Layout saved!', obj)


def get_layout_list(request):
    """ Returns a list of all the available layouts """
    if request.method != 'GET':
        return res.get_only_get_allowed({})

    layout_entries = BluesteelLayoutEntry.objects.all()

    data = {}
    data['layouts'] = []

    for layout in layout_entries:
        obj = {}
        obj['id'] = layout.id
        obj['name'] = layout.name
        obj['url'] = {}
        obj['url']['project_list'] = ViewUrlGenerator.get_layout_project_list_url(layout.id)
        data['layouts'].append(obj)

    return res.get_response(200, 'Layout list', data)
