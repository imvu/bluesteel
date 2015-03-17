""" Git Feed views """

from app.util.httpcommon import res
from app.service.gitrepo.models.GitProjectModel import GitProjectEntry
from app.service.gitrepo.models.GitBranchModel import GitBranchEntry


def get_branch_list(request, project_id):
    """ Insert new commits to a given git project """
    if request.method == 'GET':
        project_entry = GitProjectEntry.objects.filter(id=project_id).first()
        if project_entry == None:
            return res.get_response(404, 'project not found', {})

        branch_entries = GitBranchEntry.objects.filter(project=project_entry)

        branches = []
        for entry in branch_entries:
            branches.append(entry.as_object())

        return res.get_response(200, '', branches)
    else:
        return res.get_only_get_allowed({})
