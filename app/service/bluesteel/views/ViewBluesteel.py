""" Bluesteel views functions """

from app.service.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.util.httpcommon import res

def add_project_feed_url(request, project):
    project['feed_url'] = request.build_absolute_uri('/feed/commit/project/{0}/'.format(project['id']))
    return project

def get_all_layouts_urls(request):
    """ Return list of all layout in json """
    if request.method == 'GET':
        all_layouts = BluesteelLayoutEntry.objects.all()

        data = {}
        data['layouts'] = []

        for layout in all_layouts:
            data['layouts'].append(request.build_absolute_uri('/bluesteel/layout/{0}/'.format(layout.id)))

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
