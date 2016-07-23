""" Presenter views, benchmark definition page functions """

from django.core.paginator import Paginator
from app.presenter.views.helpers import ViewUrlGenerator
from app.presenter.views.helpers import ViewPrepareObjects
from app.logic.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.logic.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.logic.httpcommon import res, pag
from app.logic.httpcommon.Page import Page

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

def get_benchmark_definitions(request, page_index):
    """ Returns html for the benchmark definition page """
    def_entries = BenchmarkDefinitionEntry.objects.all()

    page = Page(DEFINITION_ITEMS_PER_PAGE, page_index)
    pager = Paginator(def_entries, page.items_per_page)
    current_page = pager.page(page.page_index)
    def_entries = current_page.object_list
    page_indices = pag.get_pagination_indices(page, PAGINATION_HALF_RANGE, pager.num_pages)

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
    data['pagination'] = ViewPrepareObjects.prepare_pagination_bench_definitions(page_indices)
    data['controls'] = get_definition_controls()
    return res.get_template_data(request, 'presenter/benchmark_definitions.html', data)

def get_benchmark_definition_edit(request, definition_id):
    """ Returns html for the benchmark definition edit page """
    data = {}
    data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])
    data['controls'] = get_definition_controls()

    def_entry = BenchmarkDefinitionEntry.objects.filter(id=definition_id).first()

    if def_entry is None:
        return res.get_template_data(request, 'presenter/not_found.html', data)

    obj = def_entry.as_object()
    obj['url'] = {}
    obj['url']['save'] = ViewUrlGenerator.get_save_benchmark_definition_url(def_entry.id)
    obj['url']['delete'] = ViewUrlGenerator.get_confirm_delete_benchmark_def_url(def_entry.id)
    obj['url']['project_info'] = ViewUrlGenerator.get_editable_projects_info_url()
    obj['layout_selection'] = get_layout_selection(def_entry.layout)
    obj['project_selection'] = get_project_selection(def_entry.layout, def_entry.project)

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
    else:
        return res.get_only_get_allowed({})
