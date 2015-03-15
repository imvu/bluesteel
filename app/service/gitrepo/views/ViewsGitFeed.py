""" Git Feed views """

from app.util.httpcommon import res
from app.util.httpcommon import val
from app.service.gitrepo.models.GitProjectModel import GitProjectEntry
from app.service.gitrepo.models.GitHashModel import GitHashEntry
from app.service.gitrepo.models.GitUserModel import GitUserEntry
from app.service.gitrepo.models.GitCommitModel import GitCommitEntry
from app.service.gitrepo.models.GitParentModel import GitParentEntry
from app.service.gitrepo.models.GitDiffModel import GitDiffEntry
from app.service.gitrepo import GitSchemas


def are_commits_unique(commit_list):
    """ Returns true if all commit hashes are unique """
    unique_hash = []
    for commit in commit_list:
        if commit['commit_hash'] in unique_hash:
            return False
        else:
            unique_hash.append(commit['commit_hash'])
    return True

def are_parent_hashes_correct(commit_list):
    """ Returns true if all parents are correct """
    unique_hash = []
    for commit in commit_list:
        unique_hash.append(commit['commit_hash'])

    for commit in commit_list:
        for parent in commit['commit_parents']:
            if parent not in unique_hash:
                return False
    return True


def insert_commits(commit_list, project):
    """ Inserts all the commits into the db """
    for commit in commit_list:
        git_hash, hash_created = GitHashEntry.objects.get_or_create(
            project=project,
            git_hash=commit['commit_hash']
        )

        git_user, user_created = GitUserEntry.objects.get_or_create(
            project=project,
            name=commit['user']['name'],
            email=commit['user']['email']
            )
        del user_created

        if hash_created:
            GitCommitEntry.objects.create(
                project=project,
                commit_hash=git_hash,
                git_user=git_user,
                commit_created_at=commit['date_creation'],
                commit_pushed_at=commit['date_commit']
            )

def insert_parents(commit_list, project):
    """ Inserts all the parents into the db """
    for commit in commit_list:
        for index, parent in enumerate(commit['commit_parents']):
            hash_parent = GitHashEntry.objects.filter(git_hash=parent).first()
            hash_son = GitHashEntry.objects.filter(git_hash=commit['commit_hash']).first()

            GitParentEntry.objects.create(
                project=project,
                parent=hash_parent,
                son=hash_son,
                order=index
            )

def insert_diffs(diffs_list, project):
    """ Inserts all the parents into the db """
    for diff in diffs_list:
        commit_son = GitCommitEntry.objects.filter(commit_hash__git_hash=diff['commit_hash_son']).first()
        commit_parent = GitCommitEntry.objects.filter(commit_hash__git_hash=diff['commit_hash_parent']).first()

        GitDiffEntry.objects.create(
            project=project,
            git_commit_son=commit_son,
            git_commit_parent=commit_parent,
            content=diff['diff']
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

        (obj_validated, val_resp_obj) = val.validate_obj_schema(post_info, GitSchemas.GIT_FEEDER_SCHEMA)
        if not obj_validated:
            return res.get_schema_failed(val_resp_obj)

        if not are_commits_unique(val_resp_obj['commits']):
            return res.get_response(400, 'Commits not unique', {})

        if not are_parent_hashes_correct(val_resp_obj['commits']):
            return res.get_response(400, 'Parents not correct', {})

        insert_commits(val_resp_obj['commits'], project_entry)
        insert_parents(val_resp_obj['commits'], project_entry)
        insert_diffs(val_resp_obj['diffs'], project_entry)

        return res.get_response(200, 'Commits added correctly', {})
    else:
        return res.get_response(400, 'Only post allowed', {})
