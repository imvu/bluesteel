""" Presenter Urls file """

from django.conf.urls import patterns, url

# pylint: disable=C0103
urlpatterns = patterns(
    '',
    url(r'^view/$',
        'app.presenter.views.ViewMain.get_main'),

    url(r'^layout/all/$',
        'app.presenter.views.ViewLayout.get_layouts'),

    url(r'^layout/edit/(?P<layout_id>\d+)/$',
        'app.presenter.views.ViewLayout.get_layout_editable'),

    url(r'^layout/(?P<layout_id>\d+)/add/project/$',
        'app.presenter.views.ViewLayout.add_default_project'),

    url(r'^layout/(?P<layout_id>\d+)/confirm/delete/$',
        'app.presenter.views.ViewLayout.confirm_delete'),

    url(r'^layout/(?P<layout_id>\d+)/save/$',
        'app.presenter.views.json.ViewJsonLayout.save_layout'),

    url(r'^layout/(?P<layout_id>\d+)/delete/$',
        'app.presenter.views.json.ViewJsonLayout.delete'),

    url(r'^layout/create/$',
        'app.presenter.views.json.ViewJsonLayout.post_create_new_layout'),

    url(r'^projects/$',
        'app.presenter.views.ViewProject.get_projects'),

    url(r'^project/(?P<project_id>\d+)/save/$',
        'app.presenter.views.ViewProject.save_project'),

    url(r'^project/(?P<project_id>\d+)/delete/$',
        'app.presenter.views.ViewProject.delete_project'),

    url(r'^project/(?P<project_id>\d+)/branch/all/$',
        'app.presenter.views.ViewProject.get_project_branches'),

    url(r'^project/(?P<project_id>\d+)/branch/(?P<branch_id>\d+)/$',
        'app.presenter.views.ViewProject.get_project_single_branch'),

    url(r'^workers/$',
        'app.presenter.views.ViewWorkers.get_workers'),

    url(r'^worker/(?P<worker_id>\d+)/report/all/$',
        'app.presenter.views.ViewWorkers.get_worker_reports'),

    url(r'^definitions/all/$',
        'app.presenter.views.ViewBenchmarkDefinitions.get_benchmark_definitions'),

    url(r'^definition/(?P<definition_id>\d+)/edit/$',
        'app.presenter.views.ViewBenchmarkDefinitions.get_benchmark_definition_edit'),

    url(r'^definitions/create/$',
        'app.presenter.views.json.ViewJsonBenchmarkDefinitions.create_new_benchmark_definition'),

    url(r'^definition/(?P<benchmark_definition_id>\d+)/save/$',
        'app.presenter.views.json.ViewJsonBenchmarkDefinitions.view_save_benchmark_definition'),
)
