""" Presenter Urls file """

from django.conf.urls import patterns, url
from django.contrib import admin

admin.autodiscover()

# pylint: disable=C0103

# disable lines too long
# pylint: disable=C0301

urlpatterns = patterns(
    '',
    url(r'^view/$',
        'app.presenter.views.html.ViewHtmlMain.get_main'),

    url(r'^layout/all/page/(?P<page_index>\d+)/$',
        'app.presenter.views.html.ViewHtmlLayout.get_layouts'),

    url(r'^layout/edit/(?P<layout_id>\d+)/$',
        'app.presenter.views.html.ViewHtmlLayout.get_layout_editable'),

    url(r'^layout/(?P<layout_id>\d+)/confirm/delete/$',
        'app.presenter.views.html.ViewHtmlLayout.confirm_delete'),

    url(r'^project/all/page/(?P<page_index>\d+)/$',
        'app.presenter.views.html.ViewHtmlProject.get_projects'),

    url(r'^project/(?P<project_id>\d+)/branch/all/depth/(?P<commit_depth>\d+)/page/(?P<page_index>\d+)/$',
        'app.presenter.views.html.ViewHtmlProject.get_project_branches'),

    url(r'^project/(?P<project_id>\d+)/branch/(?P<branch_id>\d+)/$',
        'app.presenter.views.html.ViewHtmlProject.get_project_single_branch'),

    url(r'^project/(?P<project_id>\d+)/branch/(?P<branch_id>\d+)/links/$',
        'app.presenter.views.html.ViewHtmlProject.get_project_single_branch_links'),

    url(r'^worker/all/page/(?P<page_index>\d+)/$',
        'app.presenter.views.html.ViewHtmlWorkers.get_workers'),

    url(r'^worker/(?P<worker_id>\d+)/edit/$',
        'app.presenter.views.html.ViewHtmlWorkers.get_worker_edit'),

    url(r'^bluesteelworker/(?P<worker_id>\d+)/report/all/$',
        'app.presenter.views.html.ViewHtmlWorkers.get_worker_reports'),

    url(r'^bluesteelworker/download/$',
        'app.presenter.views.html.ViewHtmlBluesteelWorker.get_worker'),

    url(r'^definitions/all/page/(?P<page_index>\d+)/$',
        'app.presenter.views.html.ViewHtmlBenchmarkDefinitions.get_benchmark_definitions'),

    url(r'^definition/(?P<definition_id>\d+)/edit/$',
        'app.presenter.views.html.ViewHtmlBenchmarkDefinitions.get_benchmark_definition_edit'),

    url(r'^definition/(?P<definition_id>\d+)/confirm/delete/$',
        'app.presenter.views.html.ViewHtmlBenchmarkDefinitions.get_benchmark_definition_confirm_delete'),

    url(r'^execution/(?P<bench_exec_id>\d+)/$',
        'app.presenter.views.html.ViewHtmlBenchmarkExecution.get_benchmark_execution'),

    url(r'^execution/(?P<bench_exec_id>\d+)/window/$',
        'app.presenter.views.html.ViewHtmlBenchmarkExecution.get_benchmark_execution_window'),

    url(r'^execution/stacked/project/(?P<project_id>\d+)/branch/(?P<branch_id>\d+)/definition/(?P<definition_id>\d+)/worker/(?P<worker_id>\d+)/page/(?P<page_index>\d+)/$',
        'app.presenter.views.html.ViewHtmlBenchmarkExecution.get_benchmark_executions_stacked'),

    url(r'^feed/report/(?P<feed_report_id>\d+)/$',
        'app.presenter.views.html.ViewHtmlFeed.get_feed_report'),

    url(r'^feed/fromworker/(?P<worker_id>\d+)/page/(?P<page_index>\d+)/$',
        'app.presenter.views.html.ViewHtmlFeed.get_feed_reports_from_worker'),

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

    url(r'^definition/(?P<benchmark_definition_id>\d+)/delete/$',
        'app.presenter.views.json.ViewJsonBenchmarkDefinitions.view_delete_benchmark_definition'),

    url(r'^execution/(?P<benchmark_execution_id>\d+)/save/$',
        'app.presenter.views.json.ViewJsonBenchmarkExecutions.save_benchmark_execution'),

    url(r'^execution/(?P<benchmark_execution_id>\d+)/invalidate/$',
        'app.presenter.views.json.ViewJsonBenchmarkExecutions.invalidate_benchmark_execution'),

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

    url(r'^bluesteelworker/(?P<worker_id>\d+)/save/',
        'app.presenter.views.json.ViewJsonBluesteelWorker.save_worker'),

    url(r'^feed/commit/project/(?P<project_id>\d+)/$',
        'app.presenter.views.json.ViewJsonGitFeeder.post_commits'),

    url(r'^branch/all/project/(?P<project_id>\d+)/$',
        'app.presenter.views.json.ViewJsonGitRepo.get_branch_list'),

    url(r'^branch/merge/target/project/(?P<project_id>\d+)/$',
        'app.presenter.views.json.ViewJsonBranchMergeTarget.set_branch_merge_target'),

    url(r'^execution/acquire/$',
        'app.presenter.views.json.ViewJsonBenchmark.acquire_benchmark_execution'),

)
