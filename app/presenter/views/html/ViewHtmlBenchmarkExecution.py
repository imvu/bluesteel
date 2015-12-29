""" Presenter views, benchmark execution page functions """

# from app.presenter.views.helpers import ViewUrlGenerator
# from app.presenter.views.helpers import ViewPrepareObjects
# from app.presenter.schemas import BenchmarkExecutionSchemas
# from app.logic.benchmark.models.BenchmarkExecutionModel import BenchmarkExecutionEntry
# from app.logic.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
# from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
# from app.logic.commandrepo.controllers.CommandController import CommandController
# from app.logic.commandrepo.models.CommandModel import CommandEntry
# from app.logic.commandrepo.models.CommandSetModel import CommandSetEntry
# from app.logic.commandrepo.models.CommandResultModel import CommandResultEntry
# from app.logic.httpcommon import res, val

# def get_benchmark_execution(request, bench_exec_id):
#     """ Returns a benchmark execution """
#     data = {}
#     data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])

#     exec_entry = BenchmarkExecutionEntry.objects.filter(id=bench_exec_id).first()

#     if exec_entry == None:
#         return res.get_template_data(request, 'presenter/not_found.html', data)

#     obj = exec_entry.as_object()
#     obj['url'] = {}
#     obj['url']['save'] = ViewUrlGenerator.get_save_benchmark_definition_url(def_entry.id)
#     obj['url']['project_info'] = ViewUrlGenerator.get_editable_projects_info_url()
#     obj['layout_selection'] = get_layout_selection(def_entry.layout)
#     obj['project_selection'] = get_project_selection(def_entry.layout, def_entry.project)

#     data['definition'] = obj

#     return res.get_template_data(request, 'presenter/benchmark_definition_edit.html', data)
