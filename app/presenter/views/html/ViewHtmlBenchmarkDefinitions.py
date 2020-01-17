""" Presenter views, benchmark definition page functions """

from app.presenter.views.helpers import ViewUrlGenerator
from app.presenter.views.helpers import ViewPrepareObjects
from app.logic.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.logic.benchmark.controllers.BenchmarkDefinitionController import BenchmarkDefinitionController
from app.logic.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.logic.httpcommon import res

DEFINITION_ITEMS_PER_PAGE = 12
PAGINATION_HALF_RANGE = 2

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

def get_layout_selection(layout_id):
    """ Return a complete list of layout selection """
    layout_entries = BluesteelLayoutEntry.objects.all().order_by('name')

    layouts = []
    for entry in layout_entries:
        obj = {}
        obj['name'] = entry.name
        obj['id'] = entry.id
        obj['selected'] = layout_id == entry.id

        layouts.append(obj)
    return layouts

def get_project_selection(layout_id, project_id):
    """ Return a complete list of project selection """
    project_entries = BluesteelProjectEntry.objects.filter(layout__id=layout_id)

    projects = []
    for prj in project_entries:
        obj = {}
        obj['name'] = prj.name
        obj['id'] = prj.id
        obj['selected'] = prj.id == project_id
        projects.append(obj)
    return projects

def get_benchmark_definition_all(request, page_index):
    """ Returns html for the benchmark definition page """

    (definitions, page_indices) = BenchmarkDefinitionController.get_benchmark_definitions_with_pagination(
        DEFINITION_ITEMS_PER_PAGE,
        page_index,
        PAGINATION_HALF_RANGE
    )

    for definition in definitions:
        definition['url'] = {}
        definition['url']['single'] = ViewUrlGenerator.get_benchmark_definition_url(definition['id'])

    data = {}
    data['definitions'] = definitions
    data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])
    data['pagination'] = ViewPrepareObjects.prepare_pagination_bench_definitions(page_indices)
    data['controls'] = get_definition_controls()
    return res.get_template_data(request, 'presenter/benchmark_definition_all.html', data)

def get_benchmark_definition(request, definition_id):
    """ Returns html for the benchmark definition page """
    data = {}
    data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])
    data['controls'] = get_definition_controls()

    def_entry = BenchmarkDefinitionController.get_benchmark_definition(definition_id)

    if def_entry is None:
        return res.get_template_data(request, 'presenter/not_found.html', data)

    obj = def_entry
    obj['url'] = {}
    obj['url']['edit'] = ViewUrlGenerator.get_edit_benchmark_definition_url(definition_id)
    obj['url']['duplicate'] = ViewUrlGenerator.get_duplicate_benchmark_definition_url(definition_id)
    obj['url']['project_info'] = ViewUrlGenerator.get_editable_projects_info_url()
    obj['layout_selection'] = get_layout_selection(def_entry['layout']['id'])
    obj['project_selection'] = get_project_selection(def_entry['layout']['id'], def_entry['project']['id'])

    # Translate priority number to name.
    obj['priority']['name'] = obj['priority']['names'][obj['priority']['current']]

    data['definition'] = obj

    return res.get_template_data(request, 'presenter/benchmark_definition.html', data)

def get_benchmark_definition_edit(request, definition_id):
    """ Returns html for the benchmark definition edit page """
    data = {}
    data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])
    data['controls'] = get_definition_controls()

    def_entry = BenchmarkDefinitionController.get_benchmark_definition(definition_id)

    if def_entry is None:
        return res.get_template_data(request, 'presenter/not_found.html', data)

    obj = def_entry
    obj['url'] = {}
    obj['url']['save'] = ViewUrlGenerator.get_save_benchmark_definition_url(definition_id)
    obj['url']['delete'] = ViewUrlGenerator.get_confirm_delete_benchmark_def_url(definition_id)
    obj['url']['project_info'] = ViewUrlGenerator.get_editable_projects_info_url()
    obj['layout_selection'] = get_layout_selection(def_entry['layout']['id'])
    obj['project_selection'] = get_project_selection(def_entry['layout']['id'], def_entry['project']['id'])

    names_and_sel = []
    count = 0
    for name in obj['priority']['names']:
        nas = {}
        nas['name'] = name
        nas['selected'] = obj['priority']['current'] == count
        count = count +1
        names_and_sel.append(nas)
    obj['priority']['names'] = names_and_sel


    data['definition'] = obj

    return res.get_template_data(request, 'presenter/benchmark_definition_edit.html', data)


def get_benchmark_definition_confirm_delete(request, definition_id):
    """ Confirm benchmark definition deletion """
    if request.method == 'GET':
        bench_def = BenchmarkDefinitionEntry.objects.filter(id=definition_id).first()
        if bench_def is None:
            return res.get_template_data(request, 'presenter/not_found.html', {})

        data = {}
        data['confirm'] = {}
        data['confirm']['title'] = 'Delete Benchmark Definition'
        data['confirm']['text'] = 'Are you sure you want to delete this Benchmark Definition ?'
        data['confirm']['url'] = {}
        data['confirm']['url']['accept'] = ViewUrlGenerator.get_delete_benchmark_definition_url(bench_def.id)
        data['confirm']['url']['cancel'] = ViewUrlGenerator.get_edit_benchmark_definition_url(bench_def.id)
        data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])

        return res.get_template_data(request, 'presenter/confirm.html', data)

    return res.get_only_get_allowed({})
