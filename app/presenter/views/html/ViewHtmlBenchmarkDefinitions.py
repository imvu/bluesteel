""" Presenter views, benchmark definition page functions """

from app.presenter.views.helpers import ViewUrlGenerator
from app.presenter.views.helpers import ViewPrepareObjects
from app.service.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.service.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.service.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.util.httpcommon import res

def get_definition_controls():
    """ Returns a list of control buttons for the benchmark definitions page """
    control = {}
    control['name'] = '  Add Definition'
    control['link'] = ViewUrlGenerator.get_create_benchmark_definitions_url()
    control['icon'] = 'fa fa-plus'
    control['onclick'] = 'create_new_benchmark_definition(this, \'{0}\');'.format(control['link'])

    controls = []
    controls.append(control)
    return controls

def get_layout_selection(layout):
    """ Return a complete list of layout selection """
    layout_entries = BluesteelLayoutEntry.objects.all().order_by('name')

    layouts = []
    for entry in layout_entries:
        obj = {}
        obj['name'] = entry.name
        obj['id'] = entry.id
        obj['selected'] = layout.id == entry.id

        layouts.append(obj)
    return layouts

def get_project_selection(layout, project):
    """ Return a complete list of project selection """
    project_entries = BluesteelProjectEntry.objects.filter(layout=layout)

    projects = []
    for prj in project_entries:
        obj = {}
        obj['name'] = prj.name
        obj['id'] = prj.id
        obj['selected'] = prj.id == project.id
        projects.append(obj)
    return projects

def get_benchmark_definitions(request):
    """ Returns html for the benchmark definition page """
    def_entries = BenchmarkDefinitionEntry.objects.all()

    definitions = []
    for entry in def_entries:
        obj = entry.as_object()
        obj['url'] = {}
        obj['url']['edit'] = ViewUrlGenerator.get_edit_benchmark_definition_url(entry.id)
        obj['url']['save'] = ViewUrlGenerator.get_save_benchmark_definition_url(entry.id)
        definitions.append(obj)

    data = {}
    data['definitions'] = definitions
    data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])
    data['controls'] = get_definition_controls()
    return res.get_template_data(request, 'presenter/benchmark_definitions.html', data)

def get_benchmark_definition_edit(request, definition_id):
    """ Returns html for the benchmark definition edit page """
    data = {}
    data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])
    data['controls'] = get_definition_controls()

    def_entry = BenchmarkDefinitionEntry.objects.filter(id=definition_id).first()

    if def_entry == None:
        return res.get_template_data(request, 'presenter/not_found.html', data)

    obj = def_entry.as_object()
    obj['url'] = {}
    obj['url']['save'] = ViewUrlGenerator.get_save_benchmark_definition_url(def_entry.id)
    obj['url']['project_info'] = ViewUrlGenerator.get_editable_projects_info_url()
    obj['layout_selection'] = get_layout_selection(def_entry.layout)
    obj['project_selection'] = get_project_selection(def_entry.layout, def_entry.project)

    data['definition'] = obj

    return res.get_template_data(request, 'presenter/benchmark_definition_edit.html', data)
