""" Bluesteel views functions """

from app.logic.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.logic.httpcommon import res

def add_project_feed_url(request, layout):
    for project in layout['projects']:
        project['feed_url'] = request.build_absolute_uri('/gitfeeder/feed/commit/project/{0}/'.format(project['id']))
    return layout

def get_all_layouts_urls(request):
    """ Return list of all layout in json """
    if request.method == 'GET':
        all_layouts = BluesteelLayoutEntry.objects.all()

        data = {}
        data['layouts'] = []

        for layout in all_layouts:
            data['layouts'].append(request.build_absolute_uri('/main/layout/{0}/'.format(layout.id)))

        return res.get_response(200, 'Layouts', data)
    else:
        return res.get_only_get_allowed({})

def get_layout(request, layout_id):
    """ Return layout in json """
    if request.method == 'GET':
        layout = BluesteelLayoutEntry.objects.all().filter(id=layout_id).first()

        if layout == None:
            return res.get_response(400, 'Layout not found', {})
        else:
            layout_obj = layout.as_object()
            layout_obj = add_project_feed_url(request, layout_obj)
            return res.get_response(200, 'Layout found', layout_obj)
    else:
        return res.get_only_get_allowed({})

def get_project_ids_and_names_from_layout(request, layout_id):
    """ Return project ids, names and selected one from a layout """
    if request.method == 'GET':
        layout = BluesteelLayoutEntry.objects.filter(id=layout_id).first()

        if layout == None:
            return res.get_response(400, 'Layout not found', {})

        project_entries = BluesteelProjectEntry.objects.filter(layout=layout).order_by('order')

        projects = []
        for index, project in enumerate(project_entries):
            obj = {}
            obj['id'] = project.id
            obj['name'] = project.name
            obj['selected'] = index == layout.project_index_path
            projects.append(obj)

        data = {}
        data['projects'] = projects

        return res.get_response(200, 'Layout projects info found', data)
    else:
        return res.get_only_get_allowed({})