""" Git Feed views """

from app.logic.httpcommon import res
from app.logic.gitrepo.models.GitProjectModel import GitProjectEntry
from app.logic.gitrepo.models.GitBranchModel import GitBranchEntry
from app.logic.gitrepo.models.GitBranchMergeTargetModel import GitBranchMergeTargetEntry

def get_branch_list(request, project_id):
    """ Insert new commits to a given git project """
    if request.method == 'GET':
        project_entry = GitProjectEntry.objects.filter(id=project_id).first()
        if project_entry is None:
            return res.get_response(404, 'project not found', {})

        branch_entries = GitBranchEntry.objects.filter(project=project_entry)

        branches = []
        for entry in branch_entries:
            obj = entry.as_object()
            merge_target_entry = GitBranchMergeTargetEntry.objects.filter(
                project=project_entry,
                current_branch=entry
            ).first()

            if merge_target_entry != None:
                obj['target_branch_name'] = merge_target_entry.target_branch.name

            branches.append(obj)

        return res.get_response(200, '', branches)
    else:
        return res.get_only_get_allowed({})
