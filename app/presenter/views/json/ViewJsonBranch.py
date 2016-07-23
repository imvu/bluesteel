""" Git Branch json views """

from app.logic.httpcommon import res
from app.logic.gitrepo.models.GitProjectModel import GitProjectEntry
from app.logic.gitrepo.models.GitBranchModel import GitBranchEntry
from app.logic.gitrepo.controllers.GitController import GitController

def update_branch_order_value(request, branch_id, project_id, order_value):
    """ Change branch order value """
    if request.method == 'POST':
        project_entry = GitProjectEntry.objects.filter(id=project_id).first()
        if project_entry is None:
            return res.get_response(404, 'project not found', {})

        branch_entry = GitBranchEntry.objects.filter(project=project_entry, id=branch_id).first()
        if branch_entry is None:
            return res.get_response(404, 'branch not found', {})

        GitController.sort_branch_with_branches(project_entry, branch_entry, order_value)

        return res.get_response(200, 'Branch order saved', {})
    else:
        return res.get_only_post_allowed({})
