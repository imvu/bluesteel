""" Git Feed views """

from django.utils import timezone
from django.conf import settings
from app.util.httpcommon import res
from app.util.httpcommon import val
from app.service.gitrepo.models.GitProjectModel import GitProjectEntry
from app.service.gitrepo.models.GitUserModel import GitUserEntry
from app.service.gitrepo.models.GitCommitModel import GitCommitEntry
from app.service.gitrepo.models.GitParentModel import GitParentEntry
from app.service.gitrepo.models.GitDiffModel import GitDiffEntry
from app.service.gitrepo.models.GitBranchModel import GitBranchEntry
from app.service.gitrepo.models.GitBranchTrailModel import GitBranchTrailEntry
from app.service.gitrepo.models.GitBranchMergeTargetModel import GitBranchMergeTargetEntry
from app.util.commandrepo.models.CommandGroupModel import CommandGroupEntry
from app.util.commandrepo.models.CommandSetModel import CommandSetEntry
from app.util.commandrepo.models.CommandModel import CommandEntry
from app.util.commandrepo.models.CommandResultModel import CommandResultEntry
from app.util.logger.models.LogModel import LogEntry
from app.service.gitfeeder.views import GitFeederSchemas
import json
import arrow
import pytz


def are_commits_unique(user, commit_list):
    """ Returns true if all commit hashes are unique """
    unique_hash = []
    for commit in commit_list:
        if commit['hash'] in unique_hash:
            msg = 'Commit {0} not unique!'.format(commit['hash'])
            LogEntry.error(user, msg)
            return (False, unique_hash)
        else:
            unique_hash.append(commit['hash'])
    return (True, unique_hash)

def are_parent_hashes_correct(user, hash_list, commit_list, project):
    """ Returns true if all parents are correct """
    for commit in commit_list:
        if len(commit['parent_hashes']) > 0:
            parent = commit['parent_hashes'][0]
            if parent in hash_list:
                continue
            else:
                try:
                    GitCommitEntry.objects.get(project=project, commit_hash=parent)
                except GitCommitEntry.DoesNotExist:
                    msg = ('Project: {0}({1})\n'
                           'Commit {2} has parent hash {3} but it is not present\n'
                          ).format(project.name, project.id, commit['hash'], parent)
                    LogEntry.error(user, msg)
                    return False
                else:
                    continue
    return True

def are_diffs_correct(user, hash_list, diffs_list, project):
    """ Returns true if all diffs are correct """
    for diff in diffs_list:
        if diff['commit_hash_son'] not in hash_list:
            commit_son_entry = GitCommitEntry.objects.filter(
                project=project,
                commit_hash=diff['commit_hash_son'],
            ).first()

            if commit_son_entry == None:
                msg = 'Commit {0} not found for diff!'.format(diff['commit_hash_son'])
                LogEntry.error(user, msg)
                return False

        if diff['commit_hash_parent'] not in hash_list:
            commit_parent_entry = GitCommitEntry.objects.filter(
                project=project,
                commit_hash=diff['commit_hash_parent'],
            ).first()

            if commit_parent_entry == None:
                msg = 'Commit {0} not found for diff!'.format(diff['commit_hash_parent'])
                LogEntry.error(user, msg)
                return False

    return True

def are_branches_correct(user, hash_list, branch_list, project):
    """ Returns true if all branches are correct """
    for branch in branch_list:
        if branch['commit_hash'] not in hash_list:
            msg = 'Branch {0} with commit {1} not found!'.format(branch['branch_name'], branch['commit_hash'])
            LogEntry.error(user, msg)
            return False

        for trail_hash in branch['trail']:
            if trail_hash not in hash_list:
                commit_trail_entry = GitCommitEntry.objects.filter(
                    project=project,
                    commit_hash=trail_hash,
                ).first()

                if commit_trail_entry == None:
                    msg = 'Trail hash {0} not found!'.format(trail_hash)
                    LogEntry.error(user, msg)
                    return False

        merge_son_hash = branch['merge_target']['diff']['commit_hash_son']
        if merge_son_hash not in hash_list:
            commit_son_entry = GitCommitEntry.objects.filter(
                project=project,
                commit_hash=merge_son_hash,
            ).first()

            if commit_son_entry == None:
                msg = 'Merge target diff son commit {0} not found!'.format(merge_son_hash)
                LogEntry.error(user, msg)
                return False

        merge_parent_hash = branch['merge_target']['diff']['commit_hash_parent']
        if merge_parent_hash not in hash_list:
            commit_parent_entry = GitCommitEntry.objects.filter(
                project=project,
                commit_hash=merge_parent_hash,
            ).first()

            if commit_parent_entry == None:
                msg = 'Merge target diff parent commit {0} not found!'.format(merge_parent_hash)
                LogEntry.error(user, msg)
                return False

        if branch['merge_target']['fork_point'] != branch['merge_target']['diff']['commit_hash_parent']:
            print 'fork_point is not the same as commit_hash_parent'
            return False

    return True

def insert_commits(commit_list, project):
    """ Inserts all the commits into the db """
    for commit in commit_list:
        try:
            GitCommitEntry.objects.get(commit_hash=commit['hash'])
        except GitCommitEntry.DoesNotExist:
            author, author_created = GitUserEntry.objects.get_or_create(
                project=project,
                name=commit['author']['name'],
                email=commit['author']['email']
                )
            committer, committer_created = GitUserEntry.objects.get_or_create(
                project=project,
                name=commit['committer']['name'],
                email=commit['committer']['email']
                )

            del author_created
            del committer_created

            GitCommitEntry.objects.create(
                project=project,
                commit_hash=commit['hash'],
                author=author,
                author_date=commit['author']['date'],
                committer=committer,
                committer_date=commit['committer']['date']
            )

def insert_parents(user, commit_list, project):
    """ Inserts all the parents into the db """
    for commit in commit_list:
        for index, parent in enumerate(commit['parent_hashes']):
            commit_parent = GitCommitEntry.objects.filter(project=project, commit_hash=parent).first()
            commit_son = GitCommitEntry.objects.filter(project=project, commit_hash=commit['hash']).first()

            if commit_parent == None:
                msg = 'Commit parent {0} not found while inserting parents!'.format(parent)
                LogEntry.error(user, msg)
                continue


            if commit_son == None:
                msg = 'Commit son {0} not found while inserting parents!'.format(commit['hash'])
                LogEntry.error(user, msg)
                continue

            parent_entry = GitParentEntry.objects.filter(project=project, parent=commit_parent, son=commit_son).first()

            if parent_entry == None:
                GitParentEntry.objects.create(
                    project=project,
                    parent=commit_parent,
                    son=commit_son,
                    order=index
                )

def insert_diffs(user, diffs_list, project):
    """ Inserts all the parents into the db """
    for diff in diffs_list:
        commit_son = GitCommitEntry.objects.filter(project=project, commit_hash=diff['commit_hash_son']).first()
        commit_parent = GitCommitEntry.objects.filter(project=project, commit_hash=diff['commit_hash_parent']).first()

        if commit_parent == None:
            msg = 'Commit parent {0} not found while inserting diffs!'.format(diff['commit_hash_parent'])
            LogEntry.error(user, msg)
            continue


        if commit_son == None:
            msg = 'Commit son {0} not found while inserting diffs!'.format(diff['commit_hash_son'])
            LogEntry.error(user, msg)
            continue

        diff_entry = GitDiffEntry.objects.filter(
            project=project,
            commit_son=commit_son,
            commit_parent=commit_parent
        ).first()

        if diff_entry == None:
            GitDiffEntry.objects.create(
                project=project,
                commit_son=commit_son,
                commit_parent=commit_parent,
                content=diff['content']
            )

def insert_branches(user, branch_list, project):
    """ Inserts all the branches into the db """
    for branch in branch_list:
        commit_entry = GitCommitEntry.objects.filter(project=project, commit_hash=branch['commit_hash']).first()
        if commit_entry == None:
            msg = 'Branch commit {0} not found!'.format(branch['commit_hash'])
            LogEntry.error(user, msg)
            continue

        try:
            branch_entry = GitBranchEntry.objects.get(project=project, name=branch['branch_name'])
        except GitBranchEntry.DoesNotExist:
            branch_entry = GitBranchEntry.objects.create(
                project=project,
                name=branch['branch_name'],
                commit=commit_entry
            )
        else:
            branch_entry.commit = commit_entry
            branch_entry.save()

def insert_branch_trails(user, branch_list, project):
    for branch in branch_list:
        branch_entry = GitBranchEntry.objects.filter(project=project, name=branch['branch_name']).first()
        if branch_entry == None:
            msg = 'Branch {0} not found while inserting trails!'.format(branch['branch_name'])
            LogEntry.error(user, msg)
            continue

        GitBranchTrailEntry.objects.filter(project=project, branch=branch_entry).delete()

        for index, git_hash in enumerate(branch['trail']):
            commit_entry = GitCommitEntry.objects.filter(project=project, commit_hash=git_hash).first()
            if commit_entry:
                GitBranchTrailEntry.objects.create(
                    project=project,
                    branch=branch_entry,
                    commit=commit_entry,
                    order=index
                )
            else:
                msg = 'Commit {0} not found while inserting branches!'.format(git_hash)
                LogEntry.error(user, msg)

def update_branch_merge_target(branch_list, project):
    """ Updates all the branch merge targets into the db """
    for branch in branch_list:

        branch_entry = GitBranchEntry.objects.get(
            commit__commit_hash=branch['commit_hash'],
            name=branch['branch_name'],
            project=project
        )

        target_entry = GitBranchEntry.objects.get(
            name=branch['merge_target']['target_branch']['name'],
            project=project
        )

        fork_point_entry = GitCommitEntry.objects.get(
            project=project,
            commit_hash=branch['merge_target']['fork_point']
        )

        son_entry = GitCommitEntry.objects.get(
            project=project,
            commit_hash=branch['merge_target']['diff']['commit_hash_son']
        )

        parent_entry = GitCommitEntry.objects.get(
            project=project,
            commit_hash=branch['merge_target']['diff']['commit_hash_parent']
        )

        diff_entry = GitDiffEntry.objects.filter(
            project=project,
            commit_son=son_entry,
            commit_parent=parent_entry
        ).first()

        if diff_entry == None:
            diff_entry = GitDiffEntry.objects.create(
                project=project,
                commit_son=son_entry,
                commit_parent=parent_entry,
                content=branch['merge_target']['diff']['content']
            )

        try:
            merge_target_entry = GitBranchMergeTargetEntry.objects.get(
                project=project,
                current_branch__name=branch['branch_name']
            )
        except GitBranchMergeTargetEntry.DoesNotExist:
            branch_entry = GitBranchMergeTargetEntry.objects.create(
                project=project,
                current_branch=branch_entry,
                target_branch=target_entry,
                fork_point=fork_point_entry,
                diff=diff_entry,
            )
        else:
            merge_target_entry.current_branch = branch_entry
            merge_target_entry.target_branch = target_entry
            merge_target_entry.fork_point = fork_point_entry
            merge_target_entry.diff = diff_entry
            merge_target_entry.save()

def insert_reports(user, reports):
    """ Inserts all the commands into the db """
    report_user = user
    if user.is_anonymous():
        report_user = None

    group_entry = CommandGroupEntry.objects.create(user=report_user)

    for command_set in reports:
        set_entry = CommandSetEntry.objects.create(group=group_entry)

        for command in command_set['commands']:
            comm_entry = CommandEntry.objects.create(
                command_set=set_entry,
                command=json.dumps(command['command']),
            )

            start_time = arrow.get(command['result']['start_time']).naive
            finish_time = arrow.get(command['result']['finish_time']).naive

            start_time = timezone.make_aware(start_time, pytz.timezone(settings.TIME_ZONE))
            finish_time = timezone.make_aware(finish_time, pytz.timezone(settings.TIME_ZONE))

            CommandResultEntry.objects.create(
                command=comm_entry,
                out=command['result']['out'],
                error=command['result']['error'],
                status=command['result']['status'],
                start_time=start_time,
                finish_time=finish_time,
            )


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

        insert_reports(request.user, val_resp_obj['reports'])

        if 'feed_data' not in val_resp_obj:
            return res.get_response(200, 'Only reports added', {})

        commits = val_resp_obj['feed_data']['commits']
        diffs = val_resp_obj['feed_data']['diffs']
        branches = val_resp_obj['feed_data']['branches']

        unique, unique_hash_list = are_commits_unique(request.user, commits)
        if not unique:
            return res.get_response(400, 'Commits not unique', {})

        if not are_parent_hashes_correct(request.user, unique_hash_list, commits, project_entry):
            return res.get_response(400, 'Parents not correct', {})

        if not are_diffs_correct(request.user, unique_hash_list, diffs, project_entry):
            return res.get_response(400, 'Diffs not correct', {})

        if not are_branches_correct(request.user, unique_hash_list, branches, project_entry):
            return res.get_response(400, 'Branches not correct', {})

        insert_commits(commits, project_entry)
        insert_parents(request.user, commits, project_entry)
        insert_diffs(request.user, diffs, project_entry)
        insert_branches(request.user, branches, project_entry)
        insert_branch_trails(request.user, branches, project_entry)
        update_branch_merge_target(branches, project_entry)

        return res.get_response(200, 'Commits added correctly', {})
    else:
        return res.get_response(400, 'Only post allowed', {})
