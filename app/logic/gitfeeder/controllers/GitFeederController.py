""" Controller for GitFeeder """

from sets import Set
from django.utils import timezone
from django.conf import settings
from app.logic.gitfeeder.models.FeedModel import FeedEntry
from app.logic.gitrepo.controllers.GitController import GitController
from app.logic.gitrepo.models.GitUserModel import GitUserEntry
from app.logic.gitrepo.models.GitCommitModel import GitCommitEntry
from app.logic.gitrepo.models.GitParentModel import GitParentEntry
from app.logic.gitrepo.models.GitDiffModel import GitDiffEntry
from app.logic.gitrepo.models.GitBranchModel import GitBranchEntry
from app.logic.gitrepo.models.GitBranchTrailModel import GitBranchTrailEntry
from app.logic.gitrepo.models.GitBranchMergeTargetModel import GitBranchMergeTargetEntry
from app.logic.commandrepo.models.CommandGroupModel import CommandGroupEntry
from app.logic.commandrepo.models.CommandSetModel import CommandSetEntry
from app.logic.commandrepo.models.CommandModel import CommandEntry
from app.logic.commandrepo.models.CommandResultModel import CommandResultEntry
from app.logic.bluesteelworker.models.WorkerModel import WorkerEntry
import arrow
import pytz

class GitFeederController(object):
    """ GitFeeder Controller """

    @staticmethod
    def check_commit(commit_hash, commit_hash_set, project):
        """ Checks if commit hash is present (in the commits list and in the DDBB) """
        if not commit_hash in commit_hash_set:
            if not GitCommitEntry.objects.filter(project=project, commit_hash=commit_hash).exists():
                return False
        return True

    @staticmethod
    def get_unique_commit_set(commit_list):
        """ Returns a set with unique commit hashes """
        commit_hash_list = []
        for commit in commit_list:
            commit_hash_list.append(commit['hash'])

        return set(commit_hash_list)


    @staticmethod
    def are_commits_unique(commit_list):
        """ Returns true if all commit hashes are unique """
        unique_hash = set()
        messages = []
        for commit in commit_list:
            if commit['hash'] in unique_hash:
                messages.append('Commit not unique {0}'.format(commit['hash']))
                return (False, messages)
            else:
                unique_hash.add(commit['hash'])
        return (True, messages)

    @staticmethod
    def are_parent_hashes_correct(commit_list, commit_hash_set, project):
        """ Returns true if all parents are correct """
        messages = []
        for commit in commit_list:
            if len(commit['parent_hashes']) > 0:
                parent_hash = commit['parent_hashes'][0]
                correct = GitFeederController.check_commit(parent_hash, commit_hash_set, project)
                if not correct:
                    messages.append('Commit {0} has parent hash {1} but it is not present'.format(
                        commit['hash'],
                        parent_hash))
                    return (False, messages)
        return (True, messages)

    @staticmethod
    def are_diffs_correct(commit_hash_set, diffs_list, project):
        """ Returns true if all diffs are correct """
        for diff in diffs_list:
            correct = GitFeederController.check_commit(diff['commit_hash_son'], commit_hash_set, project)
            if not correct:
                return (False, ['Diff with a wrong son commit {0}'.format(diff['commit_hash_son'])])

            correct = GitFeederController.check_commit(diff['commit_hash_parent'], commit_hash_set, project)
            if not correct:
                return (False, ['Diff with a wrong parent commit {0}'.format(diff['commit_hash_parent'])])
        return (True, [])


    @staticmethod
    def are_branch_trails_correct(commit_trails, commit_hash_set, project):
        """ It checks if branch trails are correct on a quick way, faster than a simple loop """
        trail_not_in_set = []

        for trail_hash in commit_trails:
            if not trail_hash in commit_hash_set:
                trail_not_in_set.append(trail_hash)

        if len(trail_not_in_set) == 0:
            return (True, [])

        trail_exist_count = GitCommitEntry.objects.filter(project=project, commit_hash__in=trail_not_in_set).count()
        if trail_exist_count == len(trail_not_in_set):
            return (True, [])

        msg = 'Trail hashes: {0}, not found!'.format(trail_not_in_set)
        return (False, [msg])


    @staticmethod
    def are_branches_correct(commit_hash_set, branch_list, project):
        """ Returns true if all branches are correct """
        for branch in branch_list:
            res = GitFeederController.check_commit(branch['commit_hash'], commit_hash_set, project)
            if not res:
                msg = 'Branch {0} with commit {1} not found!'.format(branch['branch_name'], branch['commit_hash'])
                return (False, [msg])

            res = GitFeederController.are_branch_trails_correct(branch['trail'], commit_hash_set, project)
            if not res[0]:
                return res

            com = branch['merge_target']['diff']['commit_hash_son']
            res = GitFeederController.check_commit(com, commit_hash_set, project)
            if not res:
                msg = 'Merge target diff son commit {0} not found!'.format(com)
                return (False, [msg])

            com = branch['merge_target']['diff']['commit_hash_parent']
            res = GitFeederController.check_commit(com, commit_hash_set, project)
            if not res:
                msg = 'Merge target diff parent commit {0} not found!'.format(com)
                return (False, [msg])

            fork_point = branch['merge_target']['fork_point']
            parent = branch['merge_target']['diff']['commit_hash_parent']
            if fork_point != parent:
                msg = 'fork_point ({0}) is not the same as commit_hash_parent ({1})'.format(fork_point, parent)
                return (False, [msg])

        return (True, [])

    @staticmethod
    def get_branch_names_to_remove(branch_list, project):
        """ Returns the name of those branches that needs to be deleted """
        branch_entries = GitBranchEntry.objects.filter(project=project)

        branch_list_1 = Set()
        branch_list_2 = Set()

        for branch1 in branch_list:
            branch_list_1.add(branch1['branch_name'])

        for branch2 in branch_entries:
            branch_list_2.add(branch2.name)

        return list(branch_list_2.difference(branch_list_1))


    @staticmethod
    def insert_user(project, name, email):
        """ Inserts a user on the DDBB only if it does not exist """
        author, author_created = GitUserEntry.objects.get_or_create(
            project=project,
            name=name,
            email=email
        )
        del author_created
        return author

    @staticmethod
    def insert_commits(commit_list, project):
        """ Inserts all the commits into the db """
        commit_hashes = GitCommitEntry.objects.filter(project=project).values_list('commit_hash', flat=True)

        bulk_commits = []
        for commit in commit_list:
            if commit['hash'] not in commit_hashes:
                author = GitFeederController.insert_user(project, commit['author']['name'], commit['author']['email'])
                committer = GitFeederController.insert_user(
                    project,
                    commit['committer']['name'],
                    commit['committer']['email'])

                commit = GitCommitEntry(
                    project=project,
                    commit_hash=commit['hash'],
                    author=author,
                    author_date=commit['author']['date'],
                    committer=committer,
                    committer_date=commit['committer']['date']
                )
                bulk_commits.append(commit)
        GitCommitEntry.objects.bulk_create(bulk_commits)

    @staticmethod
    def insert_parents(commit_list, project):
        """ Inserts all the parents into the db """
        messages = []
        for commit in commit_list:
            for index, parent in enumerate(commit['parent_hashes']):
                commit_parent = GitCommitEntry.objects.filter(project=project, commit_hash=parent).first()
                commit_son = GitCommitEntry.objects.filter(project=project, commit_hash=commit['hash']).first()

                if commit_parent is None:
                    messages.append('Commit parent {0} not found while inserting parents!'.format(parent))
                    continue


                if commit_son is None:
                    messages.append('Commit son {0} not found while inserting parents!'.format(commit['hash']))
                    continue

                if not GitParentEntry.objects.filter(project=project, parent=commit_parent, son=commit_son).exists():
                    GitParentEntry.objects.create(
                        project=project,
                        parent=commit_parent,
                        son=commit_son,
                        order=index
                    )
        return (True, messages)

    @staticmethod
    def insert_diffs(diffs_list, project):
        """ Inserts all the parents into the db """
        messages = []

        all_commits = list(GitCommitEntry.objects.filter(project=project))
        commits_dict = {}

        for commit in all_commits:
            commits_dict[commit.commit_hash] = commit

        for diff in diffs_list:
            if diff['commit_hash_parent'] not in commits_dict:
                messages.append('Commit parent {0} not found while inserting diffs!'.format(diff['commit_hash_parent']))
                continue


            if diff['commit_hash_son'] not in commits_dict:
                messages.append('Commit son {0} not found while inserting diffs!'.format(diff['commit_hash_son']))
                continue

            com_son = commits_dict[diff['commit_hash_son']]
            com_parent = commits_dict[diff['commit_hash_parent']]

            if not GitDiffEntry.objects.filter(project=project, commit_son=com_son, commit_parent=com_parent).exists():
                GitDiffEntry.objects.create(
                    project=project,
                    commit_son=com_son,
                    commit_parent=com_parent,
                    content=diff['content']
                )
        return (True, messages)

    @staticmethod
    def insert_branches(branch_list, project):
        """ Inserts all the branches into the db """
        messages = []
        for branch in branch_list:
            commit_entry = GitCommitEntry.objects.filter(project=project, commit_hash=branch['commit_hash']).first()
            if commit_entry is None:
                messages.append('Branch commit {0} not found!'.format(branch['commit_hash']))
                continue

            branch_entry = GitBranchEntry.objects.filter(project=project, name=branch['branch_name']).first()

            if branch_entry is None:
                branch_entry = GitBranchEntry.objects.create(
                    project=project,
                    name=branch['branch_name'],
                    commit=commit_entry
                )
                branch_entry.order = branch_entry.id
                branch_entry.save()
            else:
                branch_entry.commit = commit_entry
                branch_entry.save()

        GitController.update_branches_order_value(project)
        return (True, messages)

    @staticmethod
    def insert_branch_trails(branch_list, project):
        """ Insert branch trails and return messages if errors """
        messages = []
        bulk_trails = []

        all_commits = GitCommitEntry.objects.filter(project=project).values('id', 'commit_hash')
        commits_dict = {}

        for commit in all_commits:
            commits_dict[commit['commit_hash']] = commit['id']

        del all_commits

        for branch in branch_list:
            branch_entry = GitBranchEntry.objects.filter(project=project, name=branch['branch_name']).first()
            if branch_entry is None:
                messages.append('Branch {0} not found while inserting trails!'.format(branch['branch_name']))
                continue

            GitBranchTrailEntry.objects.filter(project=project, branch=branch_entry).delete()

            for index, git_hash in enumerate(branch['trail']):
                if git_hash in commits_dict:
                    trail = GitBranchTrailEntry(
                        project=project,
                        branch=branch_entry,
                        commit_id=commits_dict[git_hash],
                        order=index
                    )

                    bulk_trails.append(trail)
                else:
                    messages.append('Commit {0} not found while inserting branches!'.format(git_hash))

        GitBranchTrailEntry.objects.bulk_create(bulk_trails)
        return (True, messages)

    @staticmethod
    def update_branch_merge_target(branch_list, project):
        """ Updates all the branch merge targets into the db """
        for branch in branch_list:

            branch_entry = GitBranchEntry.objects.filter(
                commit__commit_hash=branch['commit_hash'],
                name=branch['branch_name'],
                project=project
            ).first()

            target_entry = GitBranchEntry.objects.filter(
                name=branch['merge_target']['target_branch']['name'],
                project=project
            ).first()

            fork_point_entry = GitCommitEntry.objects.filter(
                project=project,
                commit_hash=branch['merge_target']['fork_point']
            ).first()

            son_entry = GitCommitEntry.objects.filter(
                project=project,
                commit_hash=branch['merge_target']['diff']['commit_hash_son']
            ).first()

            parent_entry = GitCommitEntry.objects.filter(
                project=project,
                commit_hash=branch['merge_target']['diff']['commit_hash_parent']
            ).first()

            diff_entry = GitDiffEntry.objects.filter(
                project=project,
                commit_son=son_entry,
                commit_parent=parent_entry
            ).first()

            if diff_entry is None:
                diff_entry = GitDiffEntry.objects.create(
                    project=project,
                    commit_son=son_entry,
                    commit_parent=parent_entry,
                    content=branch['merge_target']['diff']['content']
                )

            merge_target_entry = GitBranchMergeTargetEntry.objects.filter(
                project=project,
                current_branch__name=branch['branch_name']
            ).first()

            if not merge_target_entry:
                GitBranchMergeTargetEntry.objects.create(
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

    @staticmethod
    def insert_reports(user, reports, project):
        """ Inserts all the commands into the db """
        report_user = user
        if user.is_anonymous():
            report_user = None

        worker_entry = WorkerEntry.objects.filter(user=report_user).first()
        group_entry = CommandGroupEntry.objects.create(user=report_user)
        feed_entry = FeedEntry.objects.create(command_group=group_entry, worker=worker_entry, git_project=project)
        del feed_entry

        for index, command_set in enumerate(reports):
            set_entry = CommandSetEntry.objects.create(
                group=group_entry,
                order=index
            )

            for index, command in enumerate(command_set['commands']):
                comm_entry = CommandEntry.objects.create(
                    command_set=set_entry,
                    command=command['command'],
                    order=index
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

    @staticmethod
    def delete_commits_of_only_branch(project, branch_name):
        """ This function will delete all the commits that are only referenced by one branch """
        branch_entry = GitBranchEntry.objects.filter(project=project, name=branch_name).first()
        if branch_entry is None:
            return

        merge_target = GitBranchMergeTargetEntry.objects.filter(project=project, current_branch=branch_entry).first()
        if merge_target is None:
            return

        trails_entries = GitBranchTrailEntry.objects.filter(project=project, branch=branch_entry).order_by('order')

        merge_fork_hash = merge_target.fork_point.commit_hash
        commits_to_delete = []

        for trail in trails_entries:
            if trail.commit.commit_hash != merge_fork_hash:
                commits_to_delete.append(trail.commit)
            else:
                break

        for commit in commits_to_delete:
            commit.delete()


    @staticmethod
    def purge_all_reports(worker_id):
        """ This function will delete all feed reports for a given  """
        FeedEntry.objects.filter(worker__id=worker_id).delete()

    @staticmethod
    def purge_old_reports(worker_id, keep_young_count):
        """ This function will delete old reports and keep some young ones """
        count = max(keep_young_count, 0)
        report_entries = FeedEntry.objects.filter(worker__id=worker_id).order_by('-created_at')[count:]

        for report in report_entries:
            report.delete()
