""" Presenter Urls file """

from django.conf.urls import patterns, url

# pylint: disable=C0103
urlpatterns = patterns(
    '',
    url(r'^view/$',
        'app.presenter.views.html.ViewHtmlMain.get_main'),

    url(r'^layout/all/$',
        'app.presenter.views.html.ViewHtmlLayout.get_layouts'),

    url(r'^layout/edit/(?P<layout_id>\d+)/$',
        'app.presenter.views.html.ViewHtmlLayout.get_layout_editable'),

    url(r'^layout/(?P<layout_id>\d+)/add/project/$',
        'app.presenter.views.html.ViewHtmlLayout.add_default_project'),

    url(r'^layout/(?P<layout_id>\d+)/confirm/delete/$',
        'app.presenter.views.html.ViewHtmlLayout.confirm_delete'),

    url(r'^layout/(?P<layout_id>\d+)/save/$',
        'app.presenter.views.json.ViewJsonLayout.save_layout'),

    url(r'^layout/(?P<layout_id>\d+)/delete/$',
        'app.presenter.views.json.ViewJsonLayout.delete'),

    url(r'^layout/create/$',
        'app.presenter.views.json.ViewJsonLayout.post_create_new_layout'),

    url(r'^projects/$',
        'app.presenter.views.html.ViewHtmlProject.get_projects'),

    url(r'^project/(?P<project_id>\d+)/save/$',
        'app.presenter.views.json.ViewJsonProject.save_project'),

    url(r'^project/(?P<project_id>\d+)/delete/$',
        'app.presenter.views.json.ViewJsonProject.delete_project'),

    url(r'^project/(?P<project_id>\d+)/branch/all/$',
        'app.presenter.views.html.ViewHtmlProject.get_project_branches'),

    url(r'^project/(?P<project_id>\d+)/branch/(?P<branch_id>\d+)/$',
        'app.presenter.views.html.ViewHtmlProject.get_project_single_branch'),

    url(r'^workers/$',
        'app.presenter.views.html.ViewHtmlWorkers.get_workers'),

    url(r'^worker/(?P<worker_id>\d+)/report/all/$',
        'app.presenter.views.html.ViewHtmlWorkers.get_worker_reports'),

    url(r'^definitions/all/$',
        'app.presenter.views.html.ViewHtmlBenchmarkDefinitions.get_benchmark_definitions'),

    url(r'^definition/(?P<definition_id>\d+)/edit/$',
        'app.presenter.views.html.ViewHtmlBenchmarkDefinitions.get_benchmark_definition_edit'),

    url(r'^definitions/create/$',
        'app.presenter.views.json.ViewJsonBenchmarkDefinitions.create_new_benchmark_definition'),

    url(r'^definition/(?P<benchmark_definition_id>\d+)/save/$',
        'app.presenter.views.json.ViewJsonBenchmarkDefinitions.view_save_benchmark_definition'),
)
