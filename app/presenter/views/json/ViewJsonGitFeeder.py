""" Git Feed json views """

import json
from django.db import transaction
from app.logic.httpcommon import res
from app.logic.httpcommon import val
from app.logic.benchmark.controllers.BenchmarkExecutionController import BenchmarkExecutionController
from app.logic.gitrepo.models.GitProjectModel import GitProjectEntry
from app.logic.gitfeeder.controllers.GitFeederController import GitFeederController
from app.logic.logger.models.LogModel import LogEntry
from app.logic.bluesteelworker.models.WorkerModel import WorkerEntry
from app.presenter.schemas import GitFeederSchemas

def post_feed_commits(request, project_id):
    """ Insert new commits to a given git project """
    if request.method == 'POST':
        project_entry = GitProjectEntry.objects.filter(id=project_id).first()
        if project_entry is None:
            return res.get_response(404, 'project not found', {})

        (json_valid, post_info) = val.validate_json_string(request.body)
        if not json_valid:
            LogEntry.error(request.user, 'Json parser failed.\n{0}'.format(json.dumps(post_info)))
            return res.get_json_parser_failed({})

        (obj_validated, val_resp_obj) = val.validate_obj_schema(post_info, GitFeederSchemas.GIT_FEED_COMMITS_SCHEMA)
        if not obj_validated:
            LogEntry.error(request.user, 'Json schema failed.\n{0}'.format(json.dumps(val_resp_obj)))
            return res.get_schema_failed(val_resp_obj)

        if 'feed_data' not in val_resp_obj:
            return res.get_response(200, 'Only reports added', {})

        commits = val_resp_obj['feed_data']['commits']
        branches = val_resp_obj['feed_data']['branches']

        commit_hash_set = GitFeederController.get_unique_commit_set(commits)

        correct, msgs = GitFeederController.are_commits_unique(commits)
        if not correct:
            LogEntry.error(request.user, (msg for msg in msgs))
            return res.get_response(400, 'Commits not correct', {})

        correct, msgs = GitFeederController.are_parent_hashes_correct(commits, commit_hash_set, project_entry)
        if not correct:
            LogEntry.error(request.user, (msg for msg in msgs))
            return res.get_response(400, 'Parents not correct', {})

        correct, msgs = GitFeederController.are_branches_correct(commit_hash_set, branches, project_entry)
        if not correct:
            LogEntry.error(request.user, (msg for msg in msgs))
            return res.get_response(400, 'Branches not correct', {})

        branches_to_remove = GitFeederController.get_branch_names_to_remove(branches, project_entry)
        for branch_name in branches_to_remove:
            GitFeederController.delete_commits_of_only_branch(project_entry, branch_name)

        GitFeederController.insert_commits(commits, project_entry)
        GitFeederController.insert_parents(commits, project_entry)
        GitFeederController.insert_branches(branches, project_entry)
        GitFeederController.insert_branch_trails(branches, project_entry)
        GitFeederController.update_branch_merge_target(branches, project_entry)

        commit_hashes = list(commit_hash_set)
        BenchmarkExecutionController.create_bench_executions_from_commits(project_entry, commit_hashes)

        return res.get_response(200, 'Commits added correctly', {})
    else:
        return res.get_response(400, 'Only post allowed', {})


def post_feed_reports(request, project_id):
    """ Insert feed reports to a given git project """
    if request.method == 'POST':
        project_entry = GitProjectEntry.objects.filter(id=project_id).first()
        if project_entry is None:
            return res.get_response(404, 'project not found', {})

        (json_valid, post_info) = val.validate_json_string(request.body)
        if not json_valid:
            LogEntry.error(request.user, 'Json parser failed.\n{0}'.format(json.dumps(post_info)))
            return res.get_json_parser_failed({})

        (obj_validated, val_resp_obj) = val.validate_obj_schema(post_info, GitFeederSchemas.GIT_FEED_REPORTS_SCHEMA)
        if not obj_validated:
            LogEntry.error(request.user, 'Json schema failed.\n{0}'.format(json.dumps(val_resp_obj)))
            return res.get_schema_failed(val_resp_obj)

        GitFeederController.insert_reports(request.user, val_resp_obj['reports'], project_entry)

        if request.user.is_authenticated() and not request.user.is_anonymous():
            worker_entry = WorkerEntry.objects.filter(user=request.user).first()

            if worker_entry:
                GitFeederController.purge_old_reports(worker_entry.id, worker_entry.max_feed_reports)

        return res.get_response(200, 'Reports added correctly', {})
    else:
        return res.get_response(400, 'Only post allowed', {})


@transaction.atomic
def purge_all_feed_reports(request, worker_id):
    """ Purge all feed reports """
    if request.method == 'POST':
        GitFeederController.purge_all_reports(worker_id)
        return res.get_response(200, 'Feed reports purged', {})
    else:
        return res.get_response(400, 'Only post allowed', {})

@transaction.atomic
def purge_old_feed_reports(request, worker_id, keep_young_count):
    """ Purge old feed reports and keep young ones"""
    if request.method == 'POST':
        GitFeederController.purge_old_reports(worker_id, keep_young_count)
        return res.get_response(200, 'Feed reports purged', {})
    else:
        return res.get_response(400, 'Only post allowed', {})
