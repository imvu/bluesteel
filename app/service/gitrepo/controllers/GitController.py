""" Git Controller file """

from app.service.gitrepo.models.GitParentModel import GitParentEntry
from app.service.gitrepo.models.GitCommitModel import GitCommitEntry
from app.service.gitrepo.models.GitUserModel import GitUserEntry
from app.service.gitrepo.models.GitBranchModel import GitBranchEntry
from app.service.gitrepo.models.GitBranchTrailModel import GitBranchTrailEntry
from app.service.gitrepo.models.GitDiffModel import GitDiffEntry
from app.service.gitrepo.models.GitBranchMergeTargetModel import GitBranchMergeTargetEntry


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
    def get_commits_from_trails(project, branch):
        """ Return commits as objects from trails """
        trails = GitBranchTrailEntry.objects.filter(project=project, branch=branch).order_by('order')
        obj = []

        for trail in trails:
            obj.append(trail.commit.as_object())
        return obj

    @staticmethod
    def get_commits_from_trails_until_fork(project, branch, fork_point_hash):
        """ Return commits as objects from trails until fork point is found """
        trails = GitBranchTrailEntry.objects.filter(project=project, branch=branch).order_by('order')
        obj = []

        for trail in trails:
            if trail.commit.commit_hash == fork_point_hash:
                break
            obj.append(trail.commit.as_object())
        return obj

    @staticmethod
    def get_branches_trimmed_by_merge_target(project):
        """ Returns branch data trimmed by its merge target information """
        branches = GitBranchEntry.objects.filter(project=project)
        ret_branches = []

        for branch in branches:
            merge_target = GitBranchMergeTargetEntry.objects.filter(project=project, current_branch=branch).first()
            if merge_target == None:
                continue

            obj = {}
            obj['name'] = branch.name
            obj['commits'] = []

            if merge_target.current_branch == merge_target.target_branch:
                obj['commits'] = GitController.get_commits_from_trails(project, branch)
            else:
                obj['commits'] = GitController.get_commits_from_trails_until_fork(
                    project,
                    branch,
                    merge_target.fork_point.commit_hash
                )

            ret_branches.append(obj)
        return ret_branches
