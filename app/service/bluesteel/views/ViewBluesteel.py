""" Bluesteel views functions """

from app.service.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.util.httpcommon import res
import os

def add_project_feed_url(request, layout):
    for project in layout['projects']:
        project['feed_url'] = request.build_absolute_uri('/gitfeeder/feed/commit/project/{0}/'.format(project['id']))
    return layout

def splitpath(path):
    """ Splits a string path on a vector of folder names """
    tmp_path = os.path.normpath(path)
    parts = []
    (tmp_path, tail) = os.path.split(tmp_path)
    while len(tmp_path) > 1 or len(tail) > 1:
        parts.append(tail)
        (tmp_path, tail) = os.path.split(tmp_path)
    parts.reverse()
    return parts

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
            layout_obj['collect_commits_path_split'] = splitpath(layout_obj['collect_commits_path'])
            return res.get_response(200, 'Layout found', layout_obj)
    else:
        return res.get_only_get_allowed({})
