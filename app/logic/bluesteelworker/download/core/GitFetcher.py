""" Git Fetcher code """

# Disable warning for relative imports
# pylint: disable=W0403

import json
import datetime
import logging as log
from CommandExecutioner import CommandExecutioner
from ProjectFolderManager import ProjectFolderManager


class GitFetcher(object):
    """
    GitFetcher is able to gather information of a git repository and return all the data with an
    understandable structure.
    """
    def __init__(self, log_level):
        """ Constructor """
        self.log_level = log_level
        self.report_stack = []
        self.branch_names = {}
        self.branch_names['remote'] = []
        self.branch_names['remove'] = []
        self.branch_names['local'] = []
        self.branch_names['names_and_hashes'] = []
        self.branch_names['names'] = []
        self.branches_data = []
        self.known_commit_hashes = []
        self.unique_commmits = []
        self.branch_list = []
        self.feed_data = {}

    def fetch_only_git_project(self, project_info):
        """ Only performs the first step to fetch the project """
        log.basicConfig(level=self.log_level)

        steps = [
            self.step_fetch_git_project,
        ]

        self.execute_steps(project_info, steps)
        return True

    def fetch_and_feed_git_project(self, project_info, known_commit_hashes):
        """ Performs fetch and all the remaining steps to feed the data """
        log.basicConfig(level=self.log_level)
        self.known_commit_hashes = known_commit_hashes

        steps = [
            self.step_fetch_git_project,
            self.step_fetch_remote_branches,
            self.step_fetch_local_branches,
            self.step_remove_local_branches,
            self.step_transform_remote_to_local_branch,
            self.step_get_all_local_branch_names,
            self.step_get_name_and_hash_from_local_branch,
            self.step_get_branches_to_remove,
            self.step_get_all_commits_from_branch,
            self.step_setup_merge_target_forevery_branch,
            self.step_setup_diff_on_merge_target,
            self.step_create_branch_trails,
            # self.step_trim_commits,
            self.step_create_unique_list_commits,
            self.step_create_branch_list,
        ]

        self.execute_steps(project_info, steps)
        return True


    def execute_steps(self, project_info, steps):
        """ Executes all the provided steps and fill the final data into the member variables """
        for step in steps:
            log.info('Step: ' + step.__name__)
            if not step(project_info):
                self.feed_data['reports'] = self.report_stack
                log.error('Step \'%s\' failed!', step.__name__)
                return False

        # Pack all the feed data
        contains_data = True
        contains_data = contains_data and (len(self.unique_commmits) > 0)
        contains_data = contains_data and (len(self.branch_list) > 0)

        if contains_data:
            self.feed_data['feed_data'] = {}
            self.feed_data['feed_data']['commits'] = self.unique_commmits
            self.feed_data['feed_data']['branches'] = self.branch_list

        self.feed_data['reports'] = self.report_stack

    def has_feed_data(self):
        return 'feed_data' in self.feed_data

    def has_branches_to_delete(self):
        return len(self.branch_names['remove']) > 0

    def step_fetch_git_project(self, project_info):
        """ Fetch a git project using project info """
        paths = GitFetcher.get_project_paths(project_info)

        if not ProjectFolderManager.is_project_folder_present(paths):
            ProjectFolderManager.create_tmp_folder_for_git_project(paths)

        if ProjectFolderManager.is_git_project_folder_present(paths):
            report = self.commands_fetch_git_project(project_info)
        else:
            report = self.commands_clone_git_project(project_info)

        self.save_report('step_fetch_git_project', report)
        if not GitFetcher.is_report_ok(report):
            return False
        return True

    def step_fetch_remote_branches(self, project_info):
        """ Fetch remote branches using project_info """
        remote_branches_report = self.commands_get_remote_branch_names(project_info)
        self.save_report('step_fetch_remote_branches', remote_branches_report)
        if not GitFetcher.is_report_ok(remote_branches_report):
            log.error('Fetch Remote Branches -- Error while fetching remote branches')
            return False

        self.branch_names['remote'] = self.extract_remote_branch_names_from_reports(remote_branches_report)

        if len(self.branch_names['remote']) == 0:
            msg = 'No remote branches found, looks strange'
            no_branches_report = GitFetcher.create_report('No command executed', 0, msg, '')
            self.save_report('step_fetch_remote_branches', no_branches_report)

        return True

    def step_fetch_local_branches(self, project_info):
        """ Fetch local branches to see how many of them need to be removed """
        local_branches_report = self.commands_get_local_branch_names(project_info)
        self.save_report('step_fetch_local_branches', local_branches_report)
        if not GitFetcher.is_report_ok(local_branches_report):
            log.error('Fetch Local Branches -- Error while fetching local branches')
            return False

        self.branch_names['local'] = self.extract_local_branch_names_from_reports(local_branches_report)

        if len(self.branch_names['local']) == 0:
            msg = 'No local branches found, looks strange'
            no_branches_report = GitFetcher.create_report('No command executed', 0, msg, '')
            self.save_report('step_fetch_local_branches', no_branches_report)

        return True

    def step_remove_local_branches(self, project_info):
        """ Removes local branches that were deleted on remote """
        branches_to_remove = []

        for local_name in self.branch_names['local']:
            found = False
            for remote_name in self.branch_names['remote']:
                if remote_name.endswith(local_name):
                    found = True
                    break

            if not found:
                branches_to_remove.append(local_name)

        removed_branches_report = self.commands_remove_branches(project_info, branches_to_remove)
        self.save_report('step_remove_local_branches', removed_branches_report)
        if not GitFetcher.is_report_ok(removed_branches_report):
            log.error('Remove Local Branches -- Error while removing local branches')
            return False
        return True

    def step_transform_remote_to_local_branch(self, project_info):
        """ Transform remote to local branches """
        remote_to_local_reports = self.checkout_remote_branches_to_local(project_info, self.branch_names['remote'])
        self.save_report('step_transform_remote_to_local_branch', remote_to_local_reports)
        if not GitFetcher.is_report_ok(remote_to_local_reports):
            return False
        return True

    def step_get_all_local_branch_names(self, project_info):
        """ Get all local branch names """
        branch_names_report = self.commands_get_local_branch_names(project_info)
        self.save_report('step_transform_remote_to_local_branch', branch_names_report)
        if not GitFetcher.is_report_ok(branch_names_report):
            return False

        self.branch_names['names'] = self.extract_branch_names_from_report(branch_names_report)
        return True

    def step_get_name_and_hash_from_local_branch(self, project_info):
        """ Get the branch names and hashes per every name """
        names_and_hashes_report = self.commands_get_branch_names_and_hashes(project_info, self.branch_names['names'])
        self.save_report('step_get_name_and_hash_from_local_branch', names_and_hashes_report)
        if not GitFetcher.is_report_ok(names_and_hashes_report):
            return False

        self.branch_names['names_and_hashes'] = self.extract_branch_names_hashes_from_report(names_and_hashes_report)
        return True

    def step_get_branches_to_remove(self, project_info):
        """ Get all the branches we will need to remove because they were deleted """
        known_names = []
        for known_branch in project_info['git']['branch']['known']:
            known_names.append(known_branch['name'])

        local_names = []
        for local_branch in self.branch_names['names_and_hashes']:
            local_names.append(local_branch['name'])

        for known in known_names:
            if known not in local_names:
                self.branch_names['remove'].append(known)

        return True

    def step_get_all_commits_from_branch(self, project_info):
        """ For every branch we get all the commits from that branch """
        for name_and_hash in self.branch_names['names_and_hashes']:
            branch_name = name_and_hash['name']
            branch_hash = name_and_hash['commit_hash']
            log.debug('Commit -- Getting all commits of: %s - %s', branch_hash, branch_name)

            com_reports = self.commands_get_commits_from_branch(project_info, branch_name)
            self.save_report('step_get_all_commits_from_branch', com_reports)
            if not GitFetcher.is_report_ok(com_reports):
                return False

            commits = self.extract_and_format_commits_from_report(com_reports)

            branch = {}
            branch['name'] = branch_name
            branch['commit_hash'] = branch_hash
            branch['commits'] = commits
            self.branches_data.append(branch)
        return True

    def step_setup_merge_target_forevery_branch(self, project_info):
        """ Setup merge_target info for each branch """
        for branch in self.branches_data:
            branch_merge_target = self.get_merge_target_from_branch_list(
                branch,
                self.branches_data,
                project_info['git']['branch']['known']
            )

            branch['merge_target'] = branch_merge_target

            for branch_target in self.branches_data:
                if branch_target['commit_hash'] == branch['merge_target']['target_branch']['commit_hash']:
                    branch['merge_target']['fork_point'] = self.get_fork_point_between_branches(
                        branch_target,
                        branch
                    )
                    break
        return True

    def step_setup_diff_on_merge_target(self, project_info):
        """ Add the diff related with the merge_target info """

        for branch in self.branches_data:
            diff_target_report = self.commands_get_diff_between_commits(
                project_info,
                branch['commit_hash'],
                branch['merge_target']['fork_point']
            )

            self.save_report('step_setup_diff_on_merge_target', diff_target_report)
            if not GitFetcher.is_report_ok(diff_target_report):
                return False

            diff_content_target = self.extract_diff_from_report(diff_target_report)
            diff = {}
            diff['commit_hash_son'] = branch['commit_hash']
            diff['commit_hash_parent'] = branch['merge_target']['fork_point']
            diff['content'] = diff_content_target
            branch['merge_target']['diff'] = diff
        return True

    def step_trim_commits(self, project_info):
        """ Trim the commits using known branches """
        for branch in self.branches_data:
            branch['commits'] = self.trim_commit_list_with_known_branches(
                branch['commits'],
                project_info['git']['branch']['known']
            )
        return True

    def step_create_branch_trails(self, project_info):
        """Create the branch trail"""
        del project_info
        for branch in self.branches_data:
            log.debug('Trails -- Creating trails for branch: %s', branch['name'])
            trail = []
            for commit in branch['commits']:
                trail.append(commit['hash'])
            branch['trail'] = trail
        return True

    def step_create_unique_list_commits(self, project_info):
        """Create a unique list of commits"""
        del project_info
        hash_dict = {}
        commits_to_check = []
        for branch in self.branches_data:
            for commit in branch['commits']:
                if commit['hash'] == branch['commit_hash']:
                    commits_to_check.append(commit)
                    continue

                if commit['hash'] == branch['merge_target']['fork_point']:
                    commits_to_check.append(commit)
                    continue

                if commit['hash'] in hash_dict:
                    continue

                if commit['hash'] in self.known_commit_hashes:
                    continue

                self.unique_commmits.append(commit)
                hash_dict[commit['hash']] = commit['hash']

        # All commits directly pointed by a Branch will be allways feeded
        for commit in commits_to_check:
            if commit['hash'] in hash_dict:
                continue

            self.unique_commmits.append(commit)
            hash_dict[commit['hash']] = commit['hash']

        return True

    def step_create_branch_list(self, project_info):
        """ Create branch list from branches_data """
        del project_info
        for branch in self.branches_data:
            branch_data = {}
            branch_data['commit_hash'] = branch['commit_hash']
            branch_data['branch_name'] = branch['name']
            branch_data['merge_target'] = branch['merge_target']
            branch_data['trail'] = branch['trail']
            self.branch_list.append(branch_data)
        return True

    def save_report(self, name, report):
        """ Save the given report or if empty save a meaningful report with some info """

        if len(report['commands']) > 0:
            self.report_stack.append(report)
        else:
            msg = 'No commands has been found. So we populate one command to let you know :D'
            rep = GitFetcher.create_report('No commands in: {0}'.format(name), 0, msg, '')
            self.report_stack.append(rep)


    @staticmethod
    def create_report(command, status, out, error):
        """ Generates a manual report in case we does not have one yet """
        report1 = {}
        report1['command'] = command
        report1['result'] = {}
        report1['result']['status'] = status
        report1['result']['out'] = out
        report1['result']['error'] = error
        report1['result']['start_time'] = datetime.datetime.utcnow().isoformat()
        report1['result']['finish_time'] = datetime.datetime.utcnow().isoformat()

        obj = {}
        obj['commands'] = []
        obj['commands'].append(report1)
        return obj

    @staticmethod
    def is_report_ok(report):
        """ Returns true if all commands status are 'OK' """
        for command in report['commands']:
            if command['result']['status'] != 0:
                return False
        return True

    @staticmethod
    def are_reports_ok(reports):
        """ Returns tru if all reports status are 'OK' """
        for report in reports:
            if not GitFetcher.is_report_ok(report):
                return False
        return True

    @staticmethod
    def get_project_paths(project_info):
        """ Returns an object with all the paths for a given project """
        paths = ProjectFolderManager.get_folder_paths(
            project_info['git']['project']['current_working_directory'],
            project_info['git']['project']['tmp_directory'],
            project_info['git']['project']['archive'],
            project_info['git']['project']['name'],
            project_info['git']['project']['git_project_search_path']
        )

        return paths

    @staticmethod
    def commands_clone_git_project(project_info):
        """ clone a git repo """
        paths = GitFetcher.get_project_paths(project_info)

        reports = CommandExecutioner.execute_command_list(
            project_info['git']['clone']['commands'],
            paths['log'],
            paths['project'],
            True
        )
        return reports

    @staticmethod
    def get_first_git_project_found_path(paths):
        """ With the project path + local_search_path returns the first path where a git project is found """
        project_cwd = ProjectFolderManager.get_cwd_of_first_git_project_found_in(paths['git_project_search_path'])
        return project_cwd

    @staticmethod
    def commands_fetch_git_project(project_info):
        """ fetch a git repo """
        paths = GitFetcher.get_project_paths(project_info)
        project_cwd = GitFetcher.get_first_git_project_found_path(paths)

        if not project_cwd:
            reports = GitFetcher.create_report(
                'git_project_search_path',
                -1,
                '',
                '{0} \nProject current working directory not found'.format(paths['git_project_search_path'])
            )
            return reports

        reports = CommandExecutioner.execute_command_list(
            project_info['git']['fetch']['commands'],
            paths['log'],
            project_cwd,
            True
        )
        return reports

    @staticmethod
    def commands_get_remote_branch_names(project_info):
        """ Returns all remote branches names """
        return GitFetcher.commands_get_branch_names(project_info, [u'git', u'branch', u'-r'])

    @staticmethod
    def commands_get_local_branch_names(project_info):
        """ Returns all local branches names """
        return GitFetcher.commands_get_branch_names(project_info, [u'git', u'branch'])

    @staticmethod
    def commands_get_branch_names(project_info, command):
        """ Returns all local branches names """
        paths = GitFetcher.get_project_paths(project_info)
        project_cwd = GitFetcher.get_first_git_project_found_path(paths)

        commands = [command]
        reports = CommandExecutioner.execute_command_list(
            commands,
            paths['log'],
            project_cwd,
            True
        )
        return reports

    @staticmethod
    def commands_remove_branches(project_info, branch_names):
        """ Returns all local branches names """
        paths = GitFetcher.get_project_paths(project_info)
        project_cwd = GitFetcher.get_first_git_project_found_path(paths)

        commands = []

        for name in branch_names:
            commands.append(['git', 'branch', '-D', name])

        reports = CommandExecutioner.execute_command_list(
            commands,
            paths['log'],
            project_cwd,
            True
        )
        return reports

    @staticmethod
    def extract_remote_branch_names_from_reports(reports):
        """ Extracts remote branch names from the reports """
        return GitFetcher.extract_branch_names_from_reports(reports, 'git branch -r')

    @staticmethod
    def extract_local_branch_names_from_reports(reports):
        """ Extracts local branch names from the reports """
        return GitFetcher.extract_branch_names_from_reports(reports, 'git branch')

    @staticmethod
    def extract_branch_names_from_reports(reports, git_command):
        """ Extracts branch names with a command from the reports """
        branch_names = []

        for command in reports['commands']:
            if command['command'] == git_command and command['result']['status'] == 0:
                names = command['result']['out'].split('\n')
                for name in names:
                    name = name.strip()

                    if len(name) == 0:
                        continue

                    if '*' in name:
                        name = name.split(' ')[1].strip()
                        if len(name) > 0:
                            branch_names.append(name)
                        continue

                    name = name.split(' ')[0].strip()
                    if len(name) > 0 and not 'HEAD' in name:
                        branch_names.append(name)

        return branch_names

    @staticmethod
    def extract_branch_names_from_report(reports):
        """ Extract a list of names from the raw branch info """
        branch_names = []

        for command in reports['commands']:
            if command['command'] == 'git branch' and command['result']['status'] == 0:
                names = command['result']['out'].split('\n')
                for name in names:
                    name = name.replace('*', '')
                    name = name.strip()
                    if len(name) > 0:
                        branch_names.append(name)
        return branch_names

    @staticmethod
    def checkout_remote_branches_to_local(project_info, remote_branch_names):
        """ Check out all the remote branches to local ones """
        paths = GitFetcher.get_project_paths(project_info)
        project_cwd = GitFetcher.get_first_git_project_found_path(paths)

        commands = []
        for name in remote_branch_names:
            name = name.split('/')
            if len(name) > 1:
                name = name[1]
            else:
                name = name[0]
            commands.append(['git', 'checkout', name])

        reports = CommandExecutioner.execute_command_list(
            commands,
            paths['log'],
            project_cwd,
            True
        )
        return reports

    @staticmethod
    def commands_get_branch_names_and_hashes(project_info, branch_names):
        """ Fetch the hash of every branch name """
        paths = GitFetcher.get_project_paths(project_info)
        project_cwd = GitFetcher.get_first_git_project_found_path(paths)

        commands = []

        for name in branch_names:
            commands.append(['git', 'rev-parse', 'refs/heads/{0}'.format(name)])

        reports = CommandExecutioner.execute_command_list(
            commands,
            paths['log'],
            project_cwd,
            True
        )
        return reports

    @staticmethod
    def extract_branch_names_hashes_from_report(reports):
        """ Extract branch names and hashesh from the reports """
        branch_names = []

        for command in reports['commands']:
            if command['command'].startswith('git rev-parse refs/heads/') and command['result']['status'] == 0:
                branch = {}
                branch['name'] = command['command'][25:].strip()
                branch['commit_hash'] = command['result']['out'].strip()
                branch_names.append(branch)
        return branch_names

    @staticmethod
    def commands_get_commits_from_branch(project_info, branch_name):
        """ Get all commits from a branch, only first parent """
        paths = GitFetcher.get_project_paths(project_info)
        project_cwd = GitFetcher.get_first_git_project_found_path(paths)

        pretty_format = {}
        pretty_format['hash'] = '%H'
        pretty_format['parent_hashes'] = '%P'
        pretty_format['author'] = {}
        pretty_format['author']['name'] = '%an'
        pretty_format['author']['email'] = '%ae'
        pretty_format['author']['date'] = '%aI'
        pretty_format['committer'] = {}
        pretty_format['committer']['name'] = '%cn'
        pretty_format['committer']['email'] = '%ce'
        pretty_format['committer']['date'] = '%cI'

        pretty_string = '--pretty=format:{0},'.format(json.dumps(pretty_format))

        commands = []
        commands.append(['git', 'reset', '--hard'])
        commands.append(['git', 'clean', '-f', '-d', '-q'])
        commands.append(['git', 'checkout', branch_name])
        commands.append(['git', 'reset', '--hard', 'origin/{0}'.format(branch_name)])
        commands.append(['git', 'log', '--first-parent', '--date=iso', pretty_string])

        reports = CommandExecutioner.execute_command_list(
            commands,
            paths['log'],
            project_cwd,
            True
        )
        return reports

    @staticmethod
    def extract_and_format_commits_from_report(reports):
        """ Transform commits from report into objects """
        commits = []

        for command in reports['commands']:
            if command['command'].startswith('git log') and command['result']['status'] == 0:
                res = command['result']['out'][:-1]
                res = res.replace('\\', '\\\\')
                commits_string = '[' + res + ']'
                commits_obj = json.loads(commits_string)

                for index, commit in enumerate(commits_obj):
                    log.debug('Commit -- Extracting commit: %s - %s', commit['hash'], index)
                    original_parents_list = commit['parent_hashes'].split(' ')
                    filtered_parents_list = []
                    for parent in original_parents_list:
                        if len(parent) > 0:
                            filtered_parents_list.append(str(parent))
                    commit['parent_hashes'] = filtered_parents_list
                    commit['author']['name'] = CommandExecutioner.remove_non_ascii(commit['author']['name'])
                    commit['author']['email'] = CommandExecutioner.remove_non_ascii(commit['author']['email'])
                    commit['committer']['name'] = CommandExecutioner.remove_non_ascii(commit['committer']['name'])
                    commit['committer']['email'] = CommandExecutioner.remove_non_ascii(commit['committer']['email'])

                commits = commits_obj
        return commits

    @staticmethod
    def trim_commit_list_with_known_branches(commits, known_branches):
        """ We trim the list of commits per branch until a known commit """
        trimmed_commits = []

        for commit in commits:
            trimmed_commits.append(commit)
            for branch in known_branches:
                if commit['hash'] == branch['commit_hash']:
                    return trimmed_commits
        return trimmed_commits

    @staticmethod
    def commands_get_fork_commit_between_branches(project_info, branch1, branch2):
        """ Get the common ancestor commit between two branches """
        paths = GitFetcher.get_project_paths(project_info)
        project_cwd = GitFetcher.get_first_git_project_found_path(paths)

        commands = [['git', 'merge-base', branch1['commit_hash'], branch2['commit_hash']]]

        reports = CommandExecutioner.execute_command_list(
            commands,
            paths['log'],
            project_cwd,
            True
        )
        return reports

    @staticmethod
    def get_merge_target_from_branch_list(branch, branch_list, known_branches):
        """
        Returns merge target branch for a given branch.
        If not found on known branches, it returns 'master' or itself
        """
        merge_target = {}
        merge_target['current_branch'] = {}
        merge_target['current_branch']['name'] = branch['name']
        merge_target['current_branch']['commit_hash'] = branch['commit_hash']
        merge_target['target_branch'] = {}
        merge_target['target_branch']['name'] = ''
        merge_target['target_branch']['commit_hash'] = ''

        for known_branch in known_branches:
            if branch['name'] == known_branch['name']:
                merge_target['target_branch']['name'] = known_branch['merge_target']['target_branch']['name']
                # We get the latest commit hash from the target branch instead of the know branch commit hash, because
                # it can be old
                commit_hash = GitFetcher.get_latests_commit_of_branch(
                    merge_target['target_branch']['name'],
                    branch_list
                )
                merge_target['target_branch']['commit_hash'] = commit_hash
                return merge_target

        for ext_branch in branch_list:
            if ext_branch['name'] == 'master':
                merge_target['target_branch']['name'] = ext_branch['name']
                merge_target['target_branch']['commit_hash'] = ext_branch['commit_hash']
                return merge_target

        merge_target['target_branch']['name'] = branch['name']
        merge_target['target_branch']['commit_hash'] = branch['commit_hash']
        return merge_target

    @staticmethod
    def get_latests_commit_of_branch(branch_name, branch_list):
        for branch in branch_list:
            if branch['name'] == branch_name:
                return branch['commit_hash']
        return ''

    @staticmethod
    def get_fork_point_between_branches(branch_target, branch_origin):
        """ Get the fork commit where two branches diverge each other """
        for commit_origin in branch_origin['commits']:
            for commit_target in branch_target['commits']:
                if commit_origin['hash'] == commit_target['hash']:
                    return commit_origin['hash']
        return ''


    @staticmethod
    def commands_get_diff_between_commits(project_info, commit_hash_1, commit_hash_2):
        """ Get the diff between 2 commits """
        paths = GitFetcher.get_project_paths(project_info)
        project_cwd = GitFetcher.get_first_git_project_found_path(paths)

        commands = [['git', 'diff', commit_hash_1, commit_hash_2]]

        reports = CommandExecutioner.execute_command_list(
            commands,
            paths['log'],
            project_cwd,
            True
        )
        return reports

    @staticmethod
    def extract_diff_from_report(reports):
        """ We extract the content of the diff from the report """

        for command in reports['commands']:
            if command['command'].startswith('git diff') and command['result']['status'] == 0:
                return command['result']['out'].decode('utf-8', 'ignore').encode('utf-8')

        return ''
