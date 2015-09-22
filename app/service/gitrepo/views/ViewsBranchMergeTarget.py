""" Git BranchMergetTarget views """

from app.util.httpcommon import res, val
from app.service.gitrepo.models.GitProjectModel import GitProjectEntry
from app.service.gitrepo.models.GitBranchModel import GitBranchEntry
from app.service.gitrepo.models.GitBranchTrailModel import GitBranchTrailEntry
from app.service.gitrepo.models.GitBranchMergeTargetModel import GitBranchMergeTargetEntry
from app.service.gitrepo.views import GitRepoSchemas


def set_branch_merge_target(request, project_id):
    """ Insert new commits to a given git project """
    if request.method == 'POST':
        project_entry = GitProjectEntry.objects.filter(id=project_id).first()
        if project_entry == None:
            return res.get_response(404, 'project not found', {})

        (json_valid, post_info) = val.validate_json_string(request.body)
        if not json_valid:
            return res.get_json_parser_failed({})

        (obj_validated, val_resp_obj) = val.validate_obj_schema(post_info, GitRepoSchemas.GIT_MERGE_TARGET_SCHEMA)
        if not obj_validated:
            return res.get_schema_failed(val_resp_obj)


        # We search for both branches involved on the merge target
        current_branch = GitBranchEntry.objects.filter(
            project=project_entry,
            name=val_resp_obj['current_branch_name']
        ).first()

        if current_branch == None:
            return res.get_response(404, 'Current branch name not found', val_resp_obj)

        target_branch = GitBranchEntry.objects.filter(
            project=project_entry,
            name=val_resp_obj['target_branch_name']
        ).first()

        if target_branch == None:
            return res.get_response(404, 'Target branch name not found', val_resp_obj)

        # We search for the merge target entry with current one
        merge_target = GitBranchMergeTargetEntry.objects.filter(
            project=project_entry,
            current_branch=current_branch,
        ).first()

        if merge_target == None:
            return res.get_response(404, 'Merge Target entry not found', val_resp_obj)

        if merge_target.target_branch.id == target_branch.id:
            return res.get_response(200, 'Target branch not changed', val_resp_obj)

        # We search for the fork point between current and target
        current_branch_trails = GitBranchTrailEntry.objects.filter(
            project=project_entry,
            branch=current_branch).order_by('-order')

        target_branch_trails = GitBranchTrailEntry.objects.filter(
            project=project_entry,
            branch=target_branch).order_by('-order')

        fork_point = None
        for index, trail in enumerate(target_branch_trails):
            if trail.commit.commit_hash != current_branch_trails[index].commit.commit_hash:
                break
            else:
                fork_point = trail.commit

        # If fork point not present, we select the first and most ancient commit of the branch
        if not fork_point:
            fork_point = current_branch_trails[-1]
            target_branch = current_branch

        merge_target.target_branch = target_branch
        merge_target.fork_point = fork_point
        merge_target.save()

        return res.get_response(200, 'Target branch changed', val_resp_obj)
    else:
        return res.get_only_post_allowed({})
