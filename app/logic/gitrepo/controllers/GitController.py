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
import sys

PAGINATION_HALF_RANGE = 2

class GitController(object):
    """ Git Controller offers functions to modify the state of git models """

    @staticmethod
    def delete_git_project(project):
        """ Delete a git project and all its components """
        project.delete()

    @staticmethod
    def wipe_project_data(project):
        """ Wipe git project data """
        GitCommitEntry.objects.filter(project=project).delete()
        GitBranchEntry.objects.filter(project=project).delete()
        GitBranchMergeTargetEntry.objects.filter(project=project).delete()
        GitBranchTrailEntry.objects.filter(project=project).delete()
        GitDiffEntry.objects.filter(project=project).delete()
        GitUserEntry.objects.filter(project=project).delete()
        GitParentEntry.objects.filter(project=project).delete()

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
    def get_branch_names_and_order_values(project):
        """ Returns a list of branch names and its order values """
        branches = GitBranchEntry.objects.filter(project=project).order_by('order')

        branches_and_order_values = []
        for branch in branches:
            obj = {}
            obj['id'] = branch.id
            obj['name'] = branch.name
            obj['order'] = branch.order
            branches_and_order_values.append(obj)
        return branches_and_order_values

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
            obj['order'] = branch.order
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
        branches = GitBranchEntry.objects.filter(project=project).order_by('order')
        return GitController.get_branches_trimmed_by_merge_target(project, branches, max_commits)

    @staticmethod
    def get_pgtd_branches_trimmed_by_merge_target(page, project, max_commits):
        """ Returns paginated branch data trimmed by its merge target information """
        branches = GitBranchEntry.objects.filter(project=project).order_by('order')

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

    @staticmethod
    def get_commit_hashes_parents_and_children(project, commit_hash, parents_children_count):
        """ Returns a window of commits hashes arround the commit_hash provided """
        parents_children_count = max(1, parents_children_count)

        commit_entry = GitCommitEntry.objects.filter(project=project, commit_hash=commit_hash).first()

        if commit_entry == None:
            return []

        current_hash = commit_entry.commit_hash
        hashes_children = []
        for i in range(parents_children_count):
            del i
            entry = GitParentEntry.objects.filter(project=project, parent__commit_hash=current_hash).first()
            if entry == None:
                break
            else:
                current_hash = entry.son.commit_hash
                hashes_children.append(current_hash)

        current_hash = commit_entry.commit_hash
        hashes_parents = []
        for i in range(parents_children_count):
            del i
            entry = GitParentEntry.objects.filter(project=project, son__commit_hash=current_hash).first()
            if entry == None:
                break
            else:
                current_hash = entry.parent.commit_hash
                hashes_parents.append(current_hash)

        return list(reversed(hashes_parents)) + [commit_entry.commit_hash] + hashes_children


    @staticmethod
    def get_best_branch_from_a_commit(project_entry, commit_hash):
        """ Returns best matching branch for a given commit_hash """
        trails = GitBranchTrailEntry.objects.filter(project=project_entry, commit__commit_hash=commit_hash)

        candidate_branches = []

        default_obj = {}
        default_obj['name'] = ''
        default_obj['order'] = int(sys.maxint)
        candidate_branches.append(default_obj)

        for trail in trails:
            merge_target = GitBranchMergeTargetEntry.objects.filter(
                project=project_entry,
                current_branch=trail.branch).first()

            if not merge_target:
                continue

            trail_fork = GitBranchTrailEntry.objects.filter(
                project=project_entry,
                commit=merge_target.fork_point).first()

            if not trail_fork:
                continue

            branch_obj = {}
            branch_obj['name'] = trail.branch.name
            branch_obj['order'] = int(trail_fork.order - trail.order)
            candidate_branches.append(branch_obj)

        candidate_branches.sort(key=lambda element: element['order'])
        return candidate_branches[0]['name']



    @staticmethod
    def update_branches_order_value(project_entry):
        """ Sort all the branches, first by order, then by updated, finally it updates order values """
        branch_entries = list(GitBranchEntry.objects.filter(project=project_entry).order_by('order', '-updated_at'))

        for index, branch in enumerate(branch_entries):
            branch.order = index
            branch.save()

    @staticmethod
    def sort_branch_with_branches(project_entry, branch_entry, branch_order):
        """ Assign new order to a given branch and then sort all of them """
        value = int(branch_order)
        if branch_entry.order <= value:
            value = value + 1

        branch_entry.order = value
        branch_entry.save()

        GitController.update_branches_order_value(project_entry)

