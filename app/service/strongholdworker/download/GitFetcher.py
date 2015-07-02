""" Git Fetcher code """

import os
import shutil
import json
import subprocess

class GitFetcher(object):
    """
    GitFetcher is able to gather information of a git repository and return all the data with an
    understandable structure.
    """
    report_stack = []
    remote_branch_names = []
    branch_names = []
    branch_names_and_hashes = []
    branches_data = []
    diff_list = []
    unique_commmits = []
    branch_list = []
    feed_data = {}

    def fetch_git_project(self, project_info):
        """ Returns an object with the repository information """

        steps = [
            self.step_fetch_git_project,
            self.step_fetch_remote_branches,
            self.step_transform_remote_to_local_branch,
            self.step_get_all_local_branch_names,
            self.step_get_name_and_hash_from_local_branch,
            self.step_get_all_commits_from_branch,
            self.step_setup_merge_target_forevery_branch,
            self.step_setup_diff_on_merge_target,
            self.step_trim_commits,
            self.step_get_diff_for_all_commits,
            self.step_create_branch_trails,
            self.step_create_unique_list_commits,
            self.step_create_branch_list,
        ]

        for step in steps:
            if not step(project_info):
                return False

        # Pack all the feed data
        self.feed_data['feed_data'] = {}
        self.feed_data['feed_data']['commits'] = self.unique_commmits
        self.feed_data['feed_data']['branches'] = self.branch_list
        self.feed_data['feed_data']['diffs'] = self.diff_list
        self.feed_data['reports'] = self.report_stack
        return True

    def step_fetch_git_project(self, project_info):
        """ Fetch a git project using project info """
        if not self.is_project_folder_present(project_info):
            self.create_tmp_folder_for_git_project(project_info)
            report = self.commands_clone_git_project(project_info)
        else:
            report = self.commands_fetch_git_project(project_info)

        self.report_stack.append(report)
        if not GitFetcher.is_report_ok(report):
            return False
        return True

    def step_fetch_remote_branches(self, project_info):
        """ Fetch remote branches using project_info """
        remote_branches_report = self.commands_get_remote_branch_names(project_info)
        self.report_stack.append(remote_branches_report)
        if not GitFetcher.is_report_ok(remote_branches_report):
            return False

        self.remote_branch_names = self.extract_remote_branch_names_from_reports(remote_branches_report)
        return True

    def step_transform_remote_to_local_branch(self, project_info):
        """ Transform remote to local branches """
        remote_to_local_reports = self.checkout_remote_branches_to_local(project_info, self.remote_branch_names)
        self.report_stack.append(remote_to_local_reports)
        if not GitFetcher.is_report_ok(remote_to_local_reports):
            return False
        return True

    def step_get_all_local_branch_names(self, project_info):
        """ Get all local branch names """
        branch_names_report = self.commands_get_branch_names(project_info)
        self.report_stack.append(branch_names_report)
        if not GitFetcher.is_report_ok(branch_names_report):
            return False

        self.branch_names = self.extract_branch_names_from_report(branch_names_report)
        return True

    def step_get_name_and_hash_from_local_branch(self, project_info):
        """ Get the branch names and hashes per every name """
        names_and_hashes_report = self.commands_get_branch_names_and_hashes(project_info, self.branch_names)
        self.report_stack.append(names_and_hashes_report)
        if not GitFetcher.is_report_ok(names_and_hashes_report):
            return False

        self.branch_names_and_hashes = self.extract_branch_names_hashes_from_report(names_and_hashes_report)
        return True

    def step_get_all_commits_from_branch(self, project_info):
        """ For every branch we get all the commits from that branch """
        for name_and_hash in self.branch_names_and_hashes:
            branch_name = name_and_hash['name']
            branch_hash = name_and_hash['hash']

            com_reports = self.commands_get_commits_from_branch(project_info, branch_name)
            self.report_stack.append(com_reports)
            if not GitFetcher.is_report_ok(com_reports):
                return False

            commits = self.extract_and_format_commits_from_report(com_reports)

            branch = {}
            branch['name'] = branch_name
            branch['hash'] = branch_hash
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
                if branch_target['hash'] == branch['merge_target']['hash']:
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
                branch['hash'],
                branch['merge_target']['fork_point']
            )

            self.report_stack.append(diff_target_report)
            if not GitFetcher.is_report_ok(diff_target_report):
                return False

            diff_content_target = self.extract_diff_from_report(diff_target_report)
            diff = {}
            diff['commit_hash_son'] = branch['hash']
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

    def step_get_diff_for_all_commits(self, project_info):
        """Get all the diffs from all the commits"""
        for branch in self.branches_data:
            for i in range(len(branch['commits']) - 1):
                commit_hash_1 = branch['commits'][i]['hash']
                commit_hash_2 = branch['commits'][i + 1]['hash']
                diff_report = self.commands_get_diff_between_commits(project_info, commit_hash_1, commit_hash_2)

                # Report check
                self.report_stack.append(diff_report)
                if not GitFetcher.is_report_ok(diff_report):
                    return False

                diff_content = self.extract_diff_from_report(diff_report)
                diff = {}
                diff['commit_hash_son'] = commit_hash_1
                diff['commit_hash_parent'] = commit_hash_2
                diff['content'] = diff_content
                self.diff_list.append(diff)
        return True

    def step_create_branch_trails(self, project_info):
        """Create the branch trail"""
        del project_info
        for branch in self.branches_data:
            trail = []
            for commit in branch['commits']:
                trail.append(commit['hash'])
            branch['trail'] = trail
        return True

    def step_create_unique_list_commits(self, project_info):
        """Create a unique list of commits"""
        del project_info
        hash_dict = {}
        for branch in self.branches_data:
            for commit in branch['commits']:
                if commit['hash'] not in hash_dict:
                    self.unique_commmits.append(commit)
                    hash_dict[commit['hash']] = commit['hash']
        return True

    def step_create_branch_list(self, project_info):
        """ Create branch list from branches_data """
        del project_info
        for branch in self.branches_data:
            branch_data = {}
            branch_data['commit_hash'] = branch['hash']
            branch_data['branch_name'] = branch['name']
            branch_data['merge_target'] = branch['merge_target']
            branch_data['trail'] = branch['trail']
            self.branch_list.append(branch_data)
        return True

    @staticmethod
    def is_report_ok(report):
        """ Returns true if all commands status are 'OK' """
        for command in report['commands']:
            if command['status'] != 'OK':
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
    def get_tmp_directory_from_list_folders(folders_list):
        return os.sep.join(folders_list)

    @staticmethod
    def get_archive_folder_path(project_info):
        current = project_info['git']['project']['current_working_directory']
        folder = GitFetcher.get_tmp_directory_from_list_folders(project_info['git']['project']['tmp_directory'])
        archive = project_info['git']['project']['archive']
        return os.path.join(current, folder, archive)

    @staticmethod
    def get_git_project_folder_path(project_info):
        """ Returns path for the git project """
        current = project_info['git']['project']['current_working_directory']
        folder = GitFetcher.get_tmp_directory_from_list_folders(project_info['git']['project']['tmp_directory'])
        archive = project_info['git']['project']['archive']
        git_name = project_info['git']['project']['name']
        return os.path.join(current, folder, archive, 'project', git_name)

    @staticmethod
    def get_cwd_of_first_git_project_found_in(directory):
        """ Searches for the first .git folder on the project path and returns its location """
        for root, dirs, files in os.walk(directory):
            del files
            for dir_to_check in dirs:
                if dir_to_check == '.git':
                    return root
        return None

    def is_project_folder_present(self, project_info):
        """ Checks if the folder structure exists """
        folder_path = self.get_archive_folder_path(project_info)
        if not os.path.exists(folder_path):
            return False
        return True

    def is_git_project_folder_present(self, project_info):
        """ Checks if the folder structure exists """
        folder_path = self.get_archive_folder_path(project_info)
        project_path = os.path.join(folder_path, 'project')
        if not os.path.exists(project_path):
            return False

        project_path = GitFetcher.get_cwd_of_first_git_project_found_in(project_path)
        if project_path == None:
            return False

        return True

    def is_log_project_folder_present(self, project_info):
        """ Checks if the folder structure exists """
        folder_path = self.get_archive_folder_path(project_info)
        if not os.path.exists(os.path.join(folder_path, 'log')):
            return False
        return True


    def create_tmp_folder_for_git_project(self, project_info):
        """ Creates git rpoject folder structure """
        folder_path = self.get_archive_folder_path(project_info)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)

        os.makedirs(os.path.join(folder_path, 'project'))
        os.makedirs(os.path.join(folder_path, 'log'))

    @staticmethod
    def clear_logs_folder(project_folder_path):
        """ Remove and re-creates the logs folder """
        logs_path = os.path.join(project_folder_path, 'log')
        if os.path.exists(logs_path):
            shutil.rmtree(logs_path)
        os.makedirs(logs_path)

    def execute_command_list(self, command_list, project_directory, project_cwd, out_file_path, err_file_path):
        """ Executes a list of commands, if the command fails it returns inmediately """
        reports = {}
        reports['commands'] = []

        for command in command_list:
            self.clear_logs_folder(project_directory)
            file_stdout = open(out_file_path, 'w')
            file_stderr = open(err_file_path, 'w')

            report = {}
            report['out'] = ''
            report['error'] = ''
            report['status'] = 'OK'

            try:
                subprocess.check_call(
                    command,
                    stdout=file_stdout,
                    stderr=file_stderr,
                    cwd=os.path.normpath(project_cwd)
                )
            except subprocess.CalledProcessError as exc:
                report['status'] = 'ERROR'
                report['exception'] = str(exc)

            file_stdout.close()
            file_stderr.close()

            file_stdout = open(out_file_path, 'r')
            file_stderr = open(err_file_path, 'r')

            report['command'] = command
            report['out'] = file_stdout.read()
            report['error'] = file_stderr.read()

            reports['commands'].append(report)

            file_stdout.close()
            file_stderr.close()

            if report['status'] == 'ERROR':
                break

        return reports

    def commands_clone_git_project(self, project_info):
        """ clone a git repo """
        folder_path = self.get_archive_folder_path(project_info)
        project_cwd = self.get_git_project_folder_path(project_info)
        stdout_path = os.path.join(folder_path, 'log', 'git_clone_stdout.txt')
        stderr_path = os.path.join(folder_path, 'log', 'git_clone_stderr.txt')

        os.makedirs(project_cwd)

        reports = self.execute_command_list(
            project_info['git']['clone']['commands'],
            str(folder_path),
            project_cwd,
            stdout_path,
            stderr_path
        )
        return reports

    def commands_fetch_git_project(self, project_info):
        """ fetch a git repo """
        folder_path = self.get_archive_folder_path(project_info)
        project_cwd = self.get_git_project_folder_path(project_info)
        project_cwd = GitFetcher.get_cwd_of_first_git_project_found_in(project_cwd)
        stdout_path = os.path.join(folder_path, 'log', 'git_clone_stdout.txt')
        stderr_path = os.path.join(folder_path, 'log', 'git_clone_stderr.txt')

        reports = self.execute_command_list(
            project_info['git']['fetch']['commands'],
            str(folder_path),
            project_cwd,
            stdout_path,
            stderr_path
        )
        return reports

    def commands_get_remote_branch_names(self, project_info):
        """ Returns all remote branches names """
        folder_path = self.get_archive_folder_path(project_info)
        project_cwd = self.get_git_project_folder_path(project_info)
        project_cwd = GitFetcher.get_cwd_of_first_git_project_found_in(project_cwd)
        stdout_path = os.path.join(folder_path, 'log', 'git_clone_stdout.txt')
        stderr_path = os.path.join(folder_path, 'log', 'git_clone_stderr.txt')

        command = [u'git', u'branch', u'-r']
        commands = []
        commands.append(command)
        reports = self.execute_command_list(commands, str(folder_path), str(project_cwd), stdout_path, stderr_path)
        return reports

    @staticmethod
    def extract_remote_branch_names_from_reports(reports):
        """ Extracts remote branch names from the reports """
        remote_branch_names = []

        for command in reports['commands']:
            if command['command'] == ['git', 'branch', '-r'] and command['status'] == 'OK':
                names = command['out'].split('\n')
                for name in names:
                    name = name.strip()
                    if len(name) == 0:
                        continue
                    name = name.split(' ')[0]
                    name = name.strip()
                    if len(name) > 0 and not 'HEAD' in name:
                        remote_branch_names.append(name)
        return remote_branch_names


    def commands_get_branch_names(self, project_info):
        """ Returns all local branches """
        folder_path = self.get_archive_folder_path(project_info)
        project_cwd = self.get_git_project_folder_path(project_info)
        project_cwd = GitFetcher.get_cwd_of_first_git_project_found_in(project_cwd)
        stdout_path = os.path.join(folder_path, 'log', 'git_clone_stdout.txt')
        stderr_path = os.path.join(folder_path, 'log', 'git_clone_stderr.txt')

        command = ['git', 'branch']
        commands = []
        commands.append(command)
        reports = self.execute_command_list(commands, str(folder_path), project_cwd, stdout_path, stderr_path)
        return reports

    @staticmethod
    def extract_branch_names_from_report(reports):
        """ Extract a list of names from the raw branch info """
        branch_names = []

        for command in reports['commands']:
            if command['command'] == ['git', 'branch'] and command['status'] == 'OK':
                names = command['out'].split('\n')
                for name in names:
                    name = name.replace('*', '')
                    name = name.strip()
                    if len(name) > 0:
                        branch_names.append(name)
        return branch_names

    def checkout_remote_branches_to_local(self, project_info, remote_branch_names):
        """ Check out all the remote branches to local ones """
        folder_path = self.get_archive_folder_path(project_info)
        project_cwd = self.get_git_project_folder_path(project_info)
        project_cwd = GitFetcher.get_cwd_of_first_git_project_found_in(project_cwd)
        stdout_path = os.path.join(folder_path, 'log', 'git_clone_stdout.txt')
        stderr_path = os.path.join(folder_path, 'log', 'git_clone_stderr.txt')

        commands = []
        for name in remote_branch_names:
            name = name.split('/')
            if len(name) > 1:
                name = name[1]
            else:
                name = name[0]

            command = ['git', 'checkout', name]
            commands.append(command)
        reports = self.execute_command_list(commands, str(folder_path), project_cwd, stdout_path, stderr_path)
        return reports

    def commands_get_branch_names_and_hashes(self, project_info, branch_names):
        """ Fetch the hash of every branch name """
        folder_path = self.get_archive_folder_path(project_info)
        project_cwd = self.get_git_project_folder_path(project_info)
        project_cwd = GitFetcher.get_cwd_of_first_git_project_found_in(project_cwd)
        stdout_path = os.path.join(folder_path, 'log', 'git_clone_stdout.txt')
        stderr_path = os.path.join(folder_path, 'log', 'git_clone_stderr.txt')

        commands = []

        for name in branch_names:
            commands.append(['git', 'rev-parse', name])

        reports = self.execute_command_list(commands, str(folder_path), project_cwd, stdout_path, stderr_path)
        return reports

    @staticmethod
    def extract_branch_names_hashes_from_report(reports):
        """ Extract branch names and hashesh from the reports """
        branch_names = []

        for command in reports['commands']:
            if command['command'][0] == 'git' and command['command'][1] == 'rev-parse' and command['status'] == 'OK':
                branch = {}
                branch['name'] = command['command'][2].strip()
                branch['hash'] = command['out'].strip()
                branch_names.append(branch)
        return branch_names

    def commands_get_commits_from_branch(self, project_info, branch_name):
        """ Get all commits from a branch, only first parent """
        folder_path = self.get_archive_folder_path(project_info)
        project_cwd = self.get_git_project_folder_path(project_info)
        project_cwd = GitFetcher.get_cwd_of_first_git_project_found_in(project_cwd)
        stdout_path = os.path.join(folder_path, 'log', 'git_clone_stdout.txt')
        stderr_path = os.path.join(folder_path, 'log', 'git_clone_stderr.txt')

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
        commands.append(['git', 'log', '--first-parent', '--date=iso', pretty_string])

        reports = self.execute_command_list(commands, str(folder_path), project_cwd, stdout_path, stderr_path)
        return reports

    @staticmethod
    def extract_and_format_commits_from_report(reports):
        """ Transform commits from report into objects """
        commits = []

        for command in reports['commands']:
            if command['command'][0] == 'git' and command['command'][1] == 'log' and command['status'] == 'OK':
                commits_string = '[' + command['out'][:-1] + ']'
                commits_obj = json.loads(commits_string)

                for commit in commits_obj:
                    commit['parent_hashes'] = commit['parent_hashes'].split(' ')
                commits = commits_obj
        return commits

    @staticmethod
    def trim_commit_list_with_known_branches(commits, known_branches):
        """ We trim the list of commits per branch until a known commit """
        trimmed_commits = []

        for commit in commits:
            trimmed_commits.append(commit)
            for branch in known_branches:
                if commit['hash'] == branch['hash']:
                    return trimmed_commits
        return trimmed_commits

    def commands_get_fork_commit_between_branches(self, project_info, branch1, branch2):
        """ Get the common ancestor commit between two branches """
        folder_path = self.get_archive_folder_path(project_info)
        project_cwd = self.get_git_project_folder_path(project_info)
        project_cwd = GitFetcher.get_cwd_of_first_git_project_found_in(project_cwd)
        stdout_path = os.path.join(folder_path, 'log', 'git_clone_stdout.txt')
        stderr_path = os.path.join(folder_path, 'log', 'git_clone_stderr.txt')

        command = ['git', 'merge-base', branch1['hash'], branch2['hash']]

        reports = self.execute_command_list([command], str(folder_path), project_cwd, stdout_path, stderr_path)
        return reports

    @staticmethod
    def get_merge_target_from_branch_list(branch, branch_list, known_branches):
        """
        Returns merge target branch for a given branch.
        If not found on known branches, it returns 'master' or itself
        """
        merge_target = {}
        merge_target['name'] = ''
        merge_target['hash'] = ''

        for known_branch in known_branches:
            if branch['name'] == known_branch['name']:
                merge_target['name'] = known_branch['merge_target']['name']
                merge_target['hash'] = known_branch['merge_target']['hash']
                return merge_target

        for ext_branch in branch_list:
            if ext_branch['name'] == 'master':
                merge_target['name'] = ext_branch['name']
                merge_target['hash'] = ext_branch['hash']
                return merge_target

        merge_target['name'] = branch['name']
        merge_target['hash'] = branch['hash']
        return merge_target

    @staticmethod
    def get_fork_point_between_branches(branch_target, branch_origin):
        """ Get the fork commit where two branches diverge each other """
        for commit_origin in branch_origin['commits']:
            for commit_target in branch_target['commits']:
                if commit_origin['hash'] == commit_target['hash']:
                    return commit_origin['hash']
        return ''


    def commands_get_diff_between_commits(self, project_info, commit_hash_1, commit_hash_2):
        """ Get the diff between 2 commits """

        folder_path = self.get_archive_folder_path(project_info)
        project_cwd = self.get_git_project_folder_path(project_info)
        project_cwd = GitFetcher.get_cwd_of_first_git_project_found_in(project_cwd)
        stdout_path = os.path.join(folder_path, 'log', 'git_clone_stdout.txt')
        stderr_path = os.path.join(folder_path, 'log', 'git_clone_stderr.txt')

        command = ['git', 'diff', commit_hash_1, commit_hash_2]

        reports = self.execute_command_list([command], str(folder_path), project_cwd, stdout_path, stderr_path)
        return reports

    @staticmethod
    def extract_diff_from_report(reports):
        """ We extract the content of the diff from the report """

        for command in reports['commands']:
            if command['command'][0] == 'git' and command['command'][1] == 'diff' and command['status'] == 'OK':
                return command['out']

        return ''

