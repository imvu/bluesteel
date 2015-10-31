""" Presenter views, benchmark definition page functions """

# from app.presenter.views import ViewUrlGenerator
from app.presenter.views import ViewPrepareObjects
# from app.service.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.util.httpcommon import res

def get_benchmark_definitions(request):
    """ Returns html for the benchmark definition page """

    # control = {}
    # control['name'] = '  Add Definition'
    # control['link'] = ViewUrlGenerator.get_layout_create_url()
    # control['icon'] = 'fa fa-plus'
    # control['onclick'] = 'create_new_layout(this, \'{0}\');'.format(control['link'])

    data = {}
    data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])
    # data['controls'] = []
    # data['controls'].append(control)

    return res.get_template_data(request, 'presenter/benchmark_definitions.html', data)
