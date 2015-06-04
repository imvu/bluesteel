""" Presenter views, layout page functions """

from app.service.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.util.httpcommon import res

def get_layout_editable(request, layout_id):
    """ Returns html for the layout editable page """
    if request.method == 'GET':
        layout = BluesteelLayoutEntry.objects.all().filter(id=layout_id).first()

        data = {}
        data['layout'] = layout.as_object()
        data['menu'] = []
        data['menu'].append({'name':'Main', 'link':'/main/view/'})
        data['menu'].append({'name':'Layout', 'link':'/main/layout/edit/0/'})
        return res.get_template_data(request, 'presenter/layout.html', data)
    else:
        return res.get_template_data(request, 'presenter/not_found.html', {})

def post_create_new_layout(request):
    """ Create a new layout and return the ID of it """
    if request.method == 'POST':
        new_layout = BluesteelLayoutEntry.objects.create_new_default_layout()

        data = {}
        data['layout'] = {}
        data['layout']['id'] = new_layout.id
        data['layout']['name'] = new_layout.name
        data['layout']['url'] = '/main/layout/edit/{0}/'.format(new_layout.id)

        return res.get_response(200, 'New layout created', data)
    else:
        return res.get_only_post_allowed({})
