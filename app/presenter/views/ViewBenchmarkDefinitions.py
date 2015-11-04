""" Presenter views, benchmark definition page functions """

from app.presenter.views import ViewUrlGenerator
from app.presenter.views import ViewPrepareObjects
from app.service.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.service.benchmark.controllers.BenchmarkDefinitionController import BenchmarkDefinitionController
from app.util.httpcommon import res

def get_benchmark_definitions(request):
    """ Returns html for the benchmark definition page """

    def_entries = BenchmarkDefinitionEntry.objects.all()

    definitions = []
    for entry in def_entries:
        definitions.append(entry.as_object())

    control = {}
    control['name'] = '  Add Definition'
    control['link'] = ViewUrlGenerator.get_create_benchmark_definitions_url()
    control['icon'] = 'fa fa-plus'
    control['onclick'] = 'create_new_benchmark_definition(this, \'{0}\');'.format(control['link'])

    data = {}
    data['definitions'] = definitions
    data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])
    data['controls'] = []
    data['controls'].append(control)

    return res.get_template_data(request, 'presenter/benchmark_definitions.html', data)


def create_new_benchmark_definition(request):
    """ Creates a new benchmark defintion """
    if request.method == 'POST':

        BenchmarkDefinitionController.create_default_benchmark_definition()

        data = {}
        data['redirect'] = ViewUrlGenerator.get_benchmark_definitions_url()

        return res.get_response(200, 'Benchmark definition created', data)
    else:
        return res.get_response(400, 'Only post allowed', {})
