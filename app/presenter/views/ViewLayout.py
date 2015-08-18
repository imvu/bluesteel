""" Presenter views, layout page functions """

from app.presenter.views import ViewHelper
from app.service.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.service.bluesteel.views import BluesteelSchemas
from app.util.httpcommon import res
from app.util.httpcommon import val

def get_save_layout_url(layout_id):
    return '/main/layout/{0}/save/'.format(layout_id)

def get_save_project_url(project_id):
    return '/main/project/{0}/save/'.format(project_id)

def get_layout_editable(request, layout_id):
    """ Returns html for the layout editable page """
    if request.method == 'GET':
        layout = BluesteelLayoutEntry.objects.all().filter(id=layout_id).first()

        data = {}
        data['layout'] = layout.as_object()
        data['menu'] = []
        data['menu'].append({'name':'Main', 'link':'/main/view/'})
        data['menu'].append({'name':'Layout', 'link':'/main/layout/edit/0/'})

        data['layout']['save_url'] = get_save_layout_url(data['layout']['id'])

        for project in data['layout']['projects']:
            project['save_url'] = get_save_project_url(project['id'])

        return res.get_template_data(request, 'presenter/layout.html', data)
    else:
        return res.get_template_data(request, 'presenter/not_found.html', {})

def post_create_new_layout(request):
    """ Create a new layout and return the ID of it """
    if request.method == 'POST':
        new_layout = BluesteelLayoutEntry.objects.create_new_default_layout()

        data = {}
        data['layout'] = new_layout.as_object()
        data['layout']['url'] = ViewHelper.create_edit_url_from_layout_id(data['layout']['id'])

        return res.get_response(200, 'New layout created', data)
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
        # Check if change of path in case we need to purge other services like 'performance tests service'
        layout_entry.collect_commits_path = val_resp_obj['collect_commits_path']
        layout_entry.save()
        return res.get_response(200, 'Layout saved', {})
    else:
        return res.get_only_post_allowed({})

