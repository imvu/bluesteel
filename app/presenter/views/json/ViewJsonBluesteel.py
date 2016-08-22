""" Bluesteel views functions """

from app.logic.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.presenter.views.helpers import ViewUrlGenerator
from app.logic.httpcommon import res

def add_project_feed_url(request, layout):
    """ Returns urls associated with every project on a given layout """
    domain = request.get_host()
    for project in layout['projects']:
        project['feed_commits_url'] = ViewUrlGenerator.get_gitfeeder_commits_full_url(domain, project['id'])
        project['feed_reports_url'] = ViewUrlGenerator.get_gitfeeder_reports_full_url(domain, project['id'])
        project['commits_hashes_url'] = ViewUrlGenerator.get_commits_known_hashes_full_url(domain, project['id'])
    return layout

def get_all_layouts_urls(request):
    """ Return list of all layout in json """
    if request.method == 'GET':
        all_layouts = BluesteelLayoutEntry.objects.all()

        data = {}
        data['layouts'] = []

        for layout in all_layouts:
            data['layouts'].append(ViewUrlGenerator.get_layout_full_url(request.get_host(), layout.id))

        return res.get_response(200, 'Layouts', data)
    else:
        return res.get_only_get_allowed({})

def get_layout(request, layout_id):
    """ Return layout in json """
    if request.method == 'GET':
        layout = BluesteelLayoutEntry.objects.filter(id=layout_id).first()

        if layout is None:
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

        if layout is None:
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
