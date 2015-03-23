""" Git Feed views """

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
from app.service.gitfeeder.views import GitFeederSchemas


def are_commits_unique(commit_list):
    """ Returns true if all commit hashes are unique """
    unique_hash = []
    for commit in commit_list:
        if commit['commit_hash'] in unique_hash:
            return (False, unique_hash)
        else:
            unique_hash.append(commit['commit_hash'])
    return (True, unique_hash)

def are_parent_hashes_correct(hash_list, commit_list):
    """ Returns true if all parents are correct """
    for commit in commit_list:
        for parent in commit['commit_parents']:
            if parent in hash_list:
                continue
            else:
                try:
                    GitCommitEntry.objects.get(commit_hash=parent)
                except GitCommitEntry.DoesNotExist:
                    return False
                else:
                    continue
    return True

def are_diffs_correct(hash_list, diffs_list, project):
    """ Returns true if all diffs are correct """
    if len(diffs_list) < len(hash_list):
        return False

    for diff in diffs_list:
        if diff['commit_hash_son'] not in hash_list:
            commit_son_entry = GitCommitEntry.objects.filter(
                project=project,
                commit_hash=diff['commit_hash_son'],
            ).first()

            if commit_son_entry == None:
                return False

        if diff['commit_hash_parent'] not in hash_list:
            commit_parent_entry = GitCommitEntry.objects.filter(
                project=project,
                commit_hash=diff['commit_hash_parent'],
            ).first()

            if commit_parent_entry == None:
                return False

    return True

def are_branches_correct(hash_list, branch_list, project):
    """ Returns true if all branches are correct """
    for branch in branch_list:
        if branch['commit_hash'] not in hash_list:
            return False

        for trail_hash in branch['trail']:
            if trail_hash not in hash_list:
                commit_trail_entry = GitCommitEntry.objects.filter(
                    project=project,
                    commit_hash=trail_hash,
                ).first()

                if commit_trail_entry == None:
                    return False

        if branch['merge_target']['diff']['commit_hash_son'] not in hash_list:
            commit_son_entry = GitCommitEntry.objects.filter(
                project=project,
                commit_hash=branch['diff']['commit_hash_son'],
            ).first()

            if commit_son_entry == None:
                print 'commit_son_entry'
                return False

        if branch['merge_target']['diff']['commit_hash_parent'] not in hash_list:
            commit_parent_entry = GitCommitEntry.objects.filter(
                project=project,
                commit_hash=branch['merge_target']['diff']['commit_hash_parent'],
            ).first()

            if commit_parent_entry == None:
                print 'commit_parent_entry'
                return False

    return True

def insert_commits(commit_list, project):
    """ Inserts all the commits into the db """
    for commit in commit_list:
        try:
            GitCommitEntry.objects.get(commit_hash=commit['commit_hash'])
        except GitCommitEntry.DoesNotExist:
            git_user, user_created = GitUserEntry.objects.get_or_create(
                project=project,
                name=commit['user']['name'],
                email=commit['user']['email']
                )
            del user_created

            GitCommitEntry.objects.create(
                project=project,
                commit_hash=commit['commit_hash'],
                git_user=git_user,
                commit_created_at=commit['date_creation'],
                commit_pushed_at=commit['date_commit']
            )

def insert_parents(commit_list, project):
    """ Inserts all the parents into the db """
    for commit in commit_list:
        for index, parent in enumerate(commit['commit_parents']):
            hash_parent = GitCommitEntry.objects.filter(commit_hash=parent).first()
            hash_son = GitCommitEntry.objects.filter(commit_hash=commit['commit_hash']).first()

            GitParentEntry.objects.create(
                project=project,
                parent=hash_parent,
                son=hash_son,
                order=index
            )

def insert_diffs(diffs_list, project):
    """ Inserts all the parents into the db """
    for diff in diffs_list:
        commit_son = GitCommitEntry.objects.filter(commit_hash=diff['commit_hash_son']).first()
        commit_parent = GitCommitEntry.objects.filter(commit_hash=diff['commit_hash_parent']).first()

        GitDiffEntry.objects.create(
            project=project,
            commit_son=commit_son,
            commit_parent=commit_parent,
            content=diff['content']
        )

def insert_branches(branch_list, project):
    """ Inserts all the branches into the db """
    for branch in branch_list:
        commit_entry = GitCommitEntry.objects.get(commit_hash=branch['commit_hash'])
        try:
            branch_entry = GitBranchEntry.objects.get(name=branch['branch_name'])
        except GitBranchEntry.DoesNotExist:
            branch_entry = GitBranchEntry.objects.create(
                project=project,
                name=branch['branch_name'],
                commit=commit_entry
            )
        else:
            branch_entry.commit = commit_entry
            branch_entry.save()

        GitBranchTrailEntry.objects.filter(branch=branch_entry).delete()

        for git_hash in branch['trail']:
            commit_entry = GitCommitEntry.objects.filter(commit_hash=git_hash).first()
            GitBranchTrailEntry.objects.create(
                project=project,
                branch=branch_entry,
                commit=commit_entry
            )

def update_branch_merge_target(branch_list, project):
    """ Updates all the branch merge targets into the db """
    for branch in branch_list:

        branch_entry = GitBranchEntry.objects.get(
            commit__commit_hash=branch['commit_hash'],
            name=branch['branch_name'],
            project=project
        )

        target_entry = GitBranchEntry.objects.get(
            name=branch['merge_target']['target_branch_name'],
            project=project
        )

        son_entry = GitCommitEntry.objects.get(
            project=project,
            commit_hash=branch['merge_target']['diff']['commit_hash_son']
            )

        parent_entry = GitCommitEntry.objects.get(
            project=project,
            commit_hash=branch['merge_target']['diff']['commit_hash_parent']
            )

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
                diff=diff_entry,
            )
        else:
            merge_target_entry.current_branch = branch_entry
            merge_target_entry.target_branch = target_entry
            merge_target_entry.diff = diff_entry
            merge_target_entry.save()


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

        unique, unique_hash_list = are_commits_unique(val_resp_obj['commits'])
        if not unique:
            return res.get_response(400, 'Commits not unique', {})

        if not are_parent_hashes_correct(unique_hash_list, val_resp_obj['commits']):
            return res.get_response(400, 'Parents not correct', {})

        if not are_diffs_correct(unique_hash_list, val_resp_obj['diffs'], project_entry):
            return res.get_response(400, 'Diffs not correct', {})

        if not are_branches_correct(unique_hash_list, val_resp_obj['branches'], project_entry):
            return res.get_response(400, 'Branches not correct', {})

        insert_commits(val_resp_obj['commits'], project_entry)
        insert_parents(val_resp_obj['commits'], project_entry)
        insert_diffs(val_resp_obj['diffs'], project_entry)
        insert_branches(val_resp_obj['branches'], project_entry)
        update_branch_merge_target(val_resp_obj['branches'], project_entry)

        return res.get_response(200, 'Commits added correctly', {})
    else:
        return res.get_response(400, 'Only post allowed', {})
