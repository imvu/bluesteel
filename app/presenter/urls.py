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

    url(r'^layout/(?P<layout_id>\d+)/confirm/delete/$',
        'app.presenter.views.html.ViewHtmlLayout.confirm_delete'),

    url(r'^projects/$',
        'app.presenter.views.html.ViewHtmlProject.get_projects'),

    url(r'^project/(?P<project_id>\d+)/branch/all/$',
        'app.presenter.views.html.ViewHtmlProject.get_project_branches'),

    url(r'^project/(?P<project_id>\d+)/branch/(?P<branch_id>\d+)/$',
        'app.presenter.views.html.ViewHtmlProject.get_project_single_branch'),

    url(r'^workers/$',
        'app.presenter.views.html.ViewHtmlWorkers.get_workers'),

    url(r'^bluesteelworker/(?P<worker_id>\d+)/report/all/$',
        'app.presenter.views.html.ViewHtmlWorkers.get_worker_reports'),

    url(r'^bluesteelworker/download/$',
        'app.presenter.views.html.ViewHtmlBluesteelWorker.get_worker'),

    url(r'^definitions/all/$',
        'app.presenter.views.html.ViewHtmlBenchmarkDefinitions.get_benchmark_definitions'),

    url(r'^definition/(?P<definition_id>\d+)/edit/$',
        'app.presenter.views.html.ViewHtmlBenchmarkDefinitions.get_benchmark_definition_edit'),

    # json views

    url(r'^layout/(?P<layout_id>\d+)/add/project/$',
        'app.presenter.views.json.ViewJsonLayout.add_default_project'),

    url(r'^layout/(?P<layout_id>\d+)/save/$',
        'app.presenter.views.json.ViewJsonLayout.save_layout'),

    url(r'^layout/(?P<layout_id>\d+)/delete/$',
        'app.presenter.views.json.ViewJsonLayout.delete'),

    url(r'^layout/create/$',
        'app.presenter.views.json.ViewJsonLayout.post_create_new_layout'),

    url(r'^layout/all/urls/$',
        'app.presenter.views.json.ViewJsonBluesteel.get_all_layouts_urls'),

    url(r'^layout/(?P<layout_id>\d+)/$',
        'app.presenter.views.json.ViewJsonBluesteel.get_layout'),

    url(r'^layout/(?P<layout_id>\d+)/projects/info/$',
        'app.presenter.views.json.ViewJsonBluesteel.get_project_ids_and_names_from_layout'),

    url(r'^project/(?P<project_id>\d+)/save/$',
        'app.presenter.views.json.ViewJsonProject.save_project'),

    url(r'^project/(?P<project_id>\d+)/delete/$',
        'app.presenter.views.json.ViewJsonProject.delete_project'),

    url(r'^definitions/create/$',
        'app.presenter.views.json.ViewJsonBenchmarkDefinitions.create_new_benchmark_definition'),

    url(r'^definition/(?P<benchmark_definition_id>\d+)/save/$',
        'app.presenter.views.json.ViewJsonBenchmarkDefinitions.view_save_benchmark_definition'),

    url(r'^bluesteelworker/bootstrap/$',
        'app.presenter.views.json.ViewJsonBluesteelWorker.get_bootstrap_urls'),

    # Using a UUID regex for a uuid3 version
    # [0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}
    url(r'^bluesteelworker/(?P<worker_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        'app.presenter.views.json.ViewJsonBluesteelWorker.get_worker_info'),

    url(r'^bluesteelworker/create/',
        'app.presenter.views.json.ViewJsonBluesteelWorker.create_worker_info'),

    url(r'^bluesteelworker/login/',
        'app.presenter.views.json.ViewJsonBluesteelWorker.login_worker_info'),

    url(r'^bluesteelworker/(?P<worker_id>\d+)/update/activity/',
        'app.presenter.views.json.ViewJsonBluesteelWorker.update_worker_activity'),

    url(r'^feed/commit/project/(?P<project_id>\d+)/$',
        'app.presenter.views.json.ViewJsonGitFeeder.post_commits'),

    url(r'^branch/all/project/(?P<project_id>\d+)/$',
        'app.presenter.views.json.ViewJsonGitRepo.get_branch_list'),

    url(r'^branch/merge/target/project/(?P<project_id>\d+)/$',
        'app.presenter.views.json.ViewJsonBranchMergeTarget.set_branch_merge_target'),

    url(r'^execution/acquire/$',
        'app.presenter.views.json.ViewJsonBenchmark.acquire_benchmark_execution'),

)
