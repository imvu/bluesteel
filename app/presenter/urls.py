""" Presenter Urls file """

from django.conf.urls import url
from django.contrib import admin
import app.presenter.views.html.ViewHtmlMain
import app.presenter.views.html.ViewHtmlLayout
import app.presenter.views.html.ViewHtmlProject
import app.presenter.views.html.ViewHtmlWorkers
import app.presenter.views.html.ViewHtmlBluesteelWorker
import app.presenter.views.html.ViewHtmlBenchmarkDefinitions
import app.presenter.views.html.ViewHtmlBenchmarkExecution
import app.presenter.views.html.ViewHtmlFeed
import app.presenter.views.html.ViewHtmlCommit
import app.presenter.views.json.ViewJsonLayout
import app.presenter.views.json.ViewJsonBluesteel
import app.presenter.views.json.ViewJsonProject
import app.presenter.views.json.ViewJsonBenchmarkDefinitions
import app.presenter.views.json.ViewJsonBenchmarkExecutions
import app.presenter.views.json.ViewJsonBluesteelWorker
import app.presenter.views.json.ViewJsonGitFeeder
import app.presenter.views.json.ViewJsonGitRepo
import app.presenter.views.json.ViewJsonBranch
import app.presenter.views.json.ViewJsonBranchMergeTarget
import app.presenter.views.json.ViewJsonBenchmark
import app.presenter.views.json.ViewJsonCommand
import app.presenter.views.json.ViewJsonNotifications

admin.autodiscover()

# pylint: disable=C0103

# disable lines too long
# pylint: disable=C0301

urlpatterns = [
    url(r'^view/$',
        app.presenter.views.html.ViewHtmlMain.get_main),

    url(r'^layout/all/page/(?P<page_index>\d+)/$',
        app.presenter.views.html.ViewHtmlLayout.get_layouts),

    url(r'^layout/edit/(?P<layout_id>\d+)/$',
        app.presenter.views.html.ViewHtmlLayout.get_layout_editable),

    url(r'^layout/(?P<layout_id>\d+)/confirm/delete/$',
        app.presenter.views.html.ViewHtmlLayout.confirm_delete),

    url(r'^layout/(?P<layout_id>\d+)/confirm/wipe/$',
        app.presenter.views.html.ViewHtmlLayout.confirm_wipe),

    url(r'^project/all/page/(?P<page_index>\d+)/$',
        app.presenter.views.html.ViewHtmlProject.get_projects),

    url(r'^project/(?P<project_id>\d+)/edit/$',
        app.presenter.views.html.ViewHtmlProject.get_project_editable),

    url(r'^project/(?P<project_id>\d+)/branch/all/depth/(?P<commit_depth>\d+)/page/(?P<page_index>\d+)/$',
        app.presenter.views.html.ViewHtmlProject.get_project_branches),

    url(r'^project/(?P<project_id>\d+)/branch/(?P<branch_id>\d+)/$',
        app.presenter.views.html.ViewHtmlProject.get_project_single_branch),

    url(r'^project/(?P<project_id>\d+)/branch/(?P<branch_id>\d+)/links/$',
        app.presenter.views.html.ViewHtmlProject.get_project_single_branch_links),

    url(r'^worker/all/page/(?P<page_index>\d+)/$',
        app.presenter.views.html.ViewHtmlWorkers.get_workers),

    url(r'^worker/(?P<worker_id>\d+)/edit/$',
        app.presenter.views.html.ViewHtmlWorkers.get_worker_edit),

    url(r'^bluesteelworker/(?P<worker_id>\d+)/report/all/$',
        app.presenter.views.html.ViewHtmlWorkers.get_worker_reports),

    url(r'^bluesteelworker/download/$',
        app.presenter.views.html.ViewHtmlBluesteelWorker.get_worker),

    url(r'^definitions/all/page/(?P<page_index>\d+)/$',
        app.presenter.views.html.ViewHtmlBenchmarkDefinitions.get_benchmark_definitions),

    url(r'^definition/(?P<definition_id>\d+)/edit/$',
        app.presenter.views.html.ViewHtmlBenchmarkDefinitions.get_benchmark_definition_edit),

    url(r'^definition/(?P<definition_id>\d+)/confirm/delete/$',
        app.presenter.views.html.ViewHtmlBenchmarkDefinitions.get_benchmark_definition_confirm_delete),

    url(r'^execution/(?P<bench_exec_id>\d+)/relevant/$',
        app.presenter.views.html.ViewHtmlBenchmarkExecution.get_benchmark_execution_relevant),

    url(r'^execution/(?P<bench_exec_id>\d+)/complete/$',
        app.presenter.views.html.ViewHtmlBenchmarkExecution.get_benchmark_execution_complete),

    url(r'^execution/(?P<bench_exec_id>\d+)/window/$',
        app.presenter.views.html.ViewHtmlBenchmarkExecution.get_benchmark_execution_window),

    url(r'^execution/stacked/project/(?P<project_id>\d+)/branch/(?P<branch_id>\d+)/definition/(?P<definition_id>\d+)/worker/(?P<worker_id>\d+)/page/(?P<page_index>\d+)/$',
        app.presenter.views.html.ViewHtmlBenchmarkExecution.get_benchmark_executions_stacked),

    url(r'^feed/report/(?P<feed_report_id>\d+)/$',
        app.presenter.views.html.ViewHtmlFeed.get_feed_report),

    url(r'^feed/fromworker/(?P<worker_id>\d+)/page/(?P<page_index>\d+)/$',
        app.presenter.views.html.ViewHtmlFeed.get_feed_reports_from_worker),

    url(r'^commit/(?P<commit_id>\d+)/ordered/worker/$',
        app.presenter.views.html.ViewHtmlCommit.get_commit_ordered_by_worker),

    # json views

    url(r'^layout/(?P<layout_id>\d+)/add/project/$',
        app.presenter.views.json.ViewJsonLayout.add_default_project),

    url(r'^layout/(?P<layout_id>\d+)/save/$',
        app.presenter.views.json.ViewJsonLayout.save_layout),

    url(r'^layout/(?P<layout_id>\d+)/delete/$',
        app.presenter.views.json.ViewJsonLayout.delete),

    url(r'^layout/(?P<layout_id>\d+)/wipe/$',
        app.presenter.views.json.ViewJsonLayout.wipe),

    url(r'^layout/create/$',
        app.presenter.views.json.ViewJsonLayout.post_create_new_layout),

    url(r'^layout/all/urls/$',
        app.presenter.views.json.ViewJsonBluesteel.get_all_layouts_urls),

    url(r'^layout/(?P<layout_id>\d+)/$',
        app.presenter.views.json.ViewJsonBluesteel.get_layout),

    url(r'^layout/(?P<layout_id>\d+)/projects/info/$',
        app.presenter.views.json.ViewJsonBluesteel.get_project_ids_and_names_from_layout),

    url(r'^project/(?P<project_id>\d+)/save/$',
        app.presenter.views.json.ViewJsonProject.save_project),

    url(r'^project/(?P<project_id>\d+)/delete/$',
        app.presenter.views.json.ViewJsonProject.delete_project),

    url(r'^definitions/create/$',
        app.presenter.views.json.ViewJsonBenchmarkDefinitions.create_new_benchmark_definition),

    url(r'^definition/(?P<benchmark_definition_id>\d+)/save/$',
        app.presenter.views.json.ViewJsonBenchmarkDefinitions.view_save_benchmark_definition),

    url(r'^definition/(?P<benchmark_definition_id>\d+)/delete/$',
        app.presenter.views.json.ViewJsonBenchmarkDefinitions.view_delete_benchmark_definition),

    url(r'^execution/(?P<benchmark_execution_id>\d+)/save/$',
        app.presenter.views.json.ViewJsonBenchmarkExecutions.save_benchmark_execution),

    url(r'^execution/(?P<benchmark_execution_id>\d+)/invalidate/$',
        app.presenter.views.json.ViewJsonBenchmarkExecutions.invalidate_benchmark_execution),

    url(r'^bluesteelworker/bootstrap/$',
        app.presenter.views.json.ViewJsonBluesteelWorker.get_bootstrap_urls),

    # Using a UUID regex for a uuid3 version
    # [0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}
    url(r'^bluesteelworker/(?P<worker_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        app.presenter.views.json.ViewJsonBluesteelWorker.get_worker_info),

    url(r'^bluesteelworker/create/',
        app.presenter.views.json.ViewJsonBluesteelWorker.create_worker_info),

    url(r'^bluesteelworker/login/',
        app.presenter.views.json.ViewJsonBluesteelWorker.login_worker_info),

    url(r'^bluesteelworker/(?P<worker_id>\d+)/update/activity/',
        app.presenter.views.json.ViewJsonBluesteelWorker.update_worker_activity),

    url(r'^bluesteelworker/(?P<worker_id>\d+)/save/',
        app.presenter.views.json.ViewJsonBluesteelWorker.save_worker),

    url(r'^feed/commit/project/(?P<project_id>\d+)/$',
        app.presenter.views.json.ViewJsonGitFeeder.post_commits),

    url(r'^feed/report/worker/(?P<worker_id>\d+)/purge/all/$',
        app.presenter.views.json.ViewJsonGitFeeder.purge_all_feed_reports),

    url(r'^feed/report/worker/(?P<worker_id>\d+)/purge/keep/(?P<keep_young_count>\d+)/$',
        app.presenter.views.json.ViewJsonGitFeeder.purge_old_feed_reports),

    url(r'^branch/all/project/(?P<project_id>\d+)/$',
        app.presenter.views.json.ViewJsonGitRepo.get_branch_list),

    url(r'^branch/(?P<branch_id>\d+)/project/(?P<project_id>\d+)/update/order/(?P<order_value>\d+)/$',
        app.presenter.views.json.ViewJsonBranch.update_branch_order_value),

    url(r'^branch/merge/target/project/(?P<project_id>\d+)/$',
        app.presenter.views.json.ViewJsonBranchMergeTarget.set_branch_merge_target),

    url(r'^execution/acquire/$',
        app.presenter.views.json.ViewJsonBenchmark.acquire_benchmark_execution),

    url(r'^command/(?P<command_id>\d+)/download/json/$',
        app.presenter.views.json.ViewJsonCommand.download_command_as_json),

    url(r'^notification/send/all/$',
        app.presenter.views.json.ViewJsonNotifications.send_notifications),
]
