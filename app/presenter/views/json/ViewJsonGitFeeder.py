""" Git Feed json views """

from django.db import transaction
from app.logic.httpcommon import res
from app.logic.httpcommon import val
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.logic.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.logic.benchmark.controllers.BenchmarkExecutionController import BenchmarkExecutionController
from app.logic.gitrepo.models.GitCommitModel import GitCommitEntry
from app.logic.gitrepo.models.GitProjectModel import GitProjectEntry
from app.logic.gitfeeder.controllers.GitFeederController import GitFeederController
from app.logic.bluesteelworker.models.WorkerModel import WorkerEntry
from app.logic.logger.models.LogModel import LogEntry
from app.presenter.schemas import GitFeederSchemas

@transaction.atomic
def post_commits(request, project_id):
    """ Insert new commits to a given git project """
    if request.method == 'POST':
        project_entry = GitProjectEntry.objects.filter(id=project_id).first()
        if project_entry == None:
            return res.get_response(404, 'project not found', {})

        (json_valid, post_info) = val.validate_json_string(request.body)
        if not json_valid:
            return res.get_json_parser_failed({})

        (obj_validated, val_resp_obj) = val.validate_obj_schema(post_info, GitFeederSchemas.GIT_FEEDER_SCHEMA)
        if not obj_validated:
            return res.get_schema_failed(val_resp_obj)

        GitFeederController.insert_reports(request.user, val_resp_obj['reports'])

        if 'feed_data' not in val_resp_obj:
            return res.get_response(200, 'Only reports added', {})

        commits = val_resp_obj['feed_data']['commits']
        diffs = val_resp_obj['feed_data']['diffs']
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

        correct, msgs = GitFeederController.are_diffs_correct(commit_hash_set, diffs, project_entry)
        if not correct:
            LogEntry.error(request.user, (msg for msg in msgs))
            return res.get_response(400, 'Diffs not correct', {})

        correct, msgs = GitFeederController.are_branches_correct(commit_hash_set, branches, project_entry)
        if not correct:
            LogEntry.error(request.user, (msg for msg in msgs))
            return res.get_response(400, 'Branches not correct', {})

        GitFeederController.insert_commits(commits, project_entry)
        GitFeederController.insert_parents(commits, project_entry)
        GitFeederController.insert_diffs(diffs, project_entry)
        GitFeederController.insert_branches(branches, project_entry)
        GitFeederController.insert_branch_trails(branches, project_entry)
        GitFeederController.update_branch_merge_target(branches, project_entry)

        project_entries = BluesteelProjectEntry.objects.filter(git_project=project_entry)
        bench_def_entries = BenchmarkDefinitionEntry.objects.filter(project__in=project_entries)
        worker_entries = WorkerEntry.objects.all()

        for commit in commits:
            commit_entry = GitCommitEntry.objects.filter(commit_hash=commit['hash'], project=project_entry).first()
            if not commit_entry:
                continue

            BenchmarkExecutionController.create_bench_executions_from_commit(
                commit_entry,
                bench_def_entries,
                worker_entries)

        return res.get_response(200, 'Commits added correctly', {})
    else:
        return res.get_response(400, 'Only post allowed', {})
