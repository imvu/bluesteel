""" Git Controller file """

from django.core.paginator import Paginator
from app.logic.httpcommon import pag
from app.logic.gitrepo.models.GitParentModel import GitParentEntry
from app.logic.gitrepo.models.GitCommitModel import GitCommitEntry
from app.logic.gitrepo.models.GitUserModel import GitUserEntry
from app.logic.gitrepo.models.GitBranchModel import GitBranchEntry
from app.logic.gitrepo.models.GitBranchTrailModel import GitBranchTrailEntry
from app.logic.gitrepo.models.GitDiffModel import GitDiffEntry
from app.logic.gitrepo.models.GitBranchMergeTargetModel import GitBranchMergeTargetEntry

PAGINATION_HALF_RANGE = 2

class GitController(object):
    """ Git Controller offers functions to modify the state of git models """

    @staticmethod
    def delete_git_project(project):
        """ Delete a git project and all its components """
        commit_entries = GitCommitEntry.objects.filter(project=project)
        branch_entries = GitBranchEntry.objects.filter(project=project)
        branch_targets = GitBranchMergeTargetEntry.objects.filter(project=project)
        branch_trails = GitBranchTrailEntry.objects.filter(project=project)
        diff_entries = GitDiffEntry.objects.filter(project=project)
        user_entries = GitUserEntry.objects.filter(project=project)
        parents_entries = GitParentEntry.objects.filter(project=project)

        for commit in commit_entries:
            commit.delete()

        for branch in branch_entries:
            branch.delete()

        for target in branch_targets:
            target.delete()

        for trail in branch_trails:
            trail.delete()

        for diff in diff_entries:
            diff.delete()

        for user in user_entries:
            user.delete()

        for parent in parents_entries:
            parent.delete()

        project.delete()

    @staticmethod
    def get_commits_from_trails(project, branch, max_commits):
        """ Return commits as objects from trails """
        max_commits = max(1, max_commits)

        trails = GitBranchTrailEntry.objects.filter(project=project, branch=branch).order_by('order')[0:max_commits]
        obj = []

        for trail in trails:
            obj.append(trail.commit.as_object())
        return obj

    @staticmethod
    def get_commits_from_trails_until_fork(project, branch, fork_point_hash, max_commits):
        """ Return commits as objects from trails until fork point is found """
        max_commits = max(1, max_commits)

        trails = GitBranchTrailEntry.objects.filter(project=project, branch=branch).order_by('order')[0:max_commits]
        obj = []

        for trail in trails:
            if trail.commit.commit_hash == fork_point_hash:
                break
            obj.append(trail.commit.as_object())
        return obj

    @staticmethod
    def get_branches_trimmed_by_merge_target(project, branches, max_commits):
        """ Returns branch data trimmed by its merge target information from branches input """
        all_branches = GitBranchEntry.objects.filter(project=project)
        ret_branches = []

        branch_names = []
        for branch in all_branches:
            branch_names.append(branch.name)

        for branch in branches:
            merge_target = GitBranchMergeTargetEntry.objects.filter(project=project, current_branch=branch).first()
            if merge_target == None:
                continue

            branch_info = []
            for branch_name in branch_names:
                obj = {}
                obj['name'] = branch_name
                obj['current_target'] = branch_name == merge_target.target_branch.name
                branch_info.append(obj)

            obj = {}
            obj['name'] = branch.name
            obj['id'] = branch.id
            obj['merge_target'] = merge_target.as_object()
            obj['branch_info'] = branch_info
            obj['commits'] = []

            if merge_target.current_branch == merge_target.target_branch:
                obj['commits'] = GitController.get_commits_from_trails(project, branch, max_commits)
            else:
                obj['commits'] = GitController.get_commits_from_trails_until_fork(
                    project,
                    branch,
                    merge_target.fork_point.commit_hash,
                    max_commits
                )

            ret_branches.append(obj)
        return ret_branches

    @staticmethod
    def get_all_branches_trimmed_by_merge_target(project, max_commits):
        """ Returns branch data trimmed by its merge target information """
        branches = GitBranchEntry.objects.filter(project=project)
        return GitController.get_branches_trimmed_by_merge_target(project, branches, max_commits)

    @staticmethod
    def get_pgtd_branches_trimmed_by_merge_target(page, project, max_commits):
        """ Returns paginated branch data trimmed by its merge target information """
        branches = GitBranchEntry.objects.filter(project=project)

        pager = Paginator(branches, page.items_per_page)
        current_page = pager.page(page.page_index)
        branches = current_page.object_list
        page_indices = pag.get_pagination_indices(page, PAGINATION_HALF_RANGE, pager.num_pages)

        branches = GitController.get_branches_trimmed_by_merge_target(project, branches, max_commits)
        return branches, page_indices

    @staticmethod
    def get_single_branch_trimmed_by_merge_target(project, branch, max_commits):
        """ Returns current and target branch data trimmed by its merge target information """
        branches = []

        merge_target = GitBranchMergeTargetEntry.objects.filter(project=project, current_branch=branch).first()
        if merge_target and merge_target.current_branch != merge_target.target_branch:
            branches.append(merge_target.target_branch)

        branches.append(branch)

        return GitController.get_branches_trimmed_by_merge_target(project, branches, max_commits)

    @staticmethod
    def get_fork_point(trails_a, trails_b):
        """ Returns the last common commit between 2 branch trails """
        fork_point = None

        if len(trails_a) > len(trails_b):
            long_list = trails_a
            short_list = trails_b
        else:
            long_list = trails_b
            short_list = trails_a

        for index, trail in enumerate(short_list):
            if trail.commit.commit_hash != long_list[index].commit.commit_hash:
                break
            else:
                fork_point = trail.commit
        return fork_point
