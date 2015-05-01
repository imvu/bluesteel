""" Git Fetcher code """

import os
import shutil
import json
import subprocess

import pprint

def fetch_git_project(project_info):
    """ Returns an object with the repository information """
    report_stack = []

    pp = pprint.PrettyPrinter(depth=6)

    # We fetch the git project
    if not is_project_folder_present(project_info):
        create_tmp_folder_for_git_project(project_info)
        report = commands_clone_git_project(project_info)
    else:
        report = commands_fetch_git_project(project_info)

    # Report check
    report_stack.append(report)
    if not report['status']:
        return report_stack

    remote_branches_report = commands_get_remote_branch_names(project_info)
    remote_branch_names = extract_remote_branch_names_from_reports(remote_branches_report)
    remote_to_local_reports = checkout_remote_branches_to_local(project_info, remote_branch_names)

    # We get the list of branches (name and hash)
    branch_names_report = commands_get_branch_names(project_info)
    branch_names = extract_branch_names_from_report(branch_names_report)

    # Report check
    report_stack.append(report)
    if not report['status']:
        return report_stack

    names_and_hashes_report = commands_get_branch_names_and_hashes(project_info, branch_names)
    names_and_hashes = extract_branch_names_and_hashes_from_report(names_and_hashes_report)

    # For every branch we get all the commits from that branch
    branches_data = []
    for name_and_hash in names_and_hashes:
        branch_name = name_and_hash['name']
        branch_hash = name_and_hash['hash']
        com_reports = commands_get_commits_from_branch(project_info, branch_name, branch_hash)

        # Report check
        report_stack.append(report)
        if not report['status']:
            return report_stack

        commits = extract_and_format_commits_from_report(com_reports)

        branch = {}
        branch['name'] = branch_name
        branch['hash'] = branch_hash
        branch['commits'] = commits
        branches_data.append(branch)


    # We setup merge_target info for each branch
    for branch in branches_data:
        branch_merge_target = get_merge_target_from_branch_list(branch, branches_data, project_info['git']['branch']['known'])
        branch['merge_target'] = branch_merge_target

        for branch_target in branches_data:

            print 'branch_target[hash]: ', branch_target['hash']
            print 'branch_target[merge_target][hash]: ', branch['merge_target']['hash']

            if branch_target['hash'] == branch['merge_target']['hash']:
                branch['merge_target']['fork_point'] = get_fork_point_between_branches(branch_target, branch)
                break

    # We add the diff related with the merge_target info
    for branch in branches_data:
        diff_report_target = commands_get_diff_between_commits(project_info, branch['hash'], branch['merge_target']['fork_point'])

        # Report check
        report_stack.append(report)
        if not report['status']:
            return report_stack

        diff_content_target = extract_diff_from_report(diff_report_target)
        diff = {}
        diff['commit_hash_son'] = branch['hash']
        diff['commit_hash_parent'] = branch['merge_target']['fork_point']
        diff['content'] = diff_content_target
        branch['merge_target']['diff'] = diff

    # We trim the commits using known branches
    for branch in branches_data:
        branch['commits'] = trim_commit_list_with_known_branches(branch['commits'], project_info['git']['branch']['known'])

    # We get all the diffs from all the commits
    diff_list = []
    for branch in branches_data:
        for i in range(len(branch['commits']) - 1):
            commit_hash_1 = branch['commits'][i]['commit']
            commit_hash_2 = branch['commits'][i + 1]['commit']
            diff_report = commands_get_diff_between_commits(project_info, commit_hash_1, commit_hash_2)

            # Report check
            report_stack.append(report)
            if not report['status']:
                return report_stack

            diff_content = extract_diff_from_report(diff_report)
            diff = {}
            diff['commit_hash_son'] = commit_hash_1
            diff['commit_hash_parent'] = commit_hash_2
            diff['content'] = diff_content
            diff_list.append(diff)

    # We create the branch trail
    for branch in branches_data:
        trail = []
        for commit in branch['commits']:
            trail.append(commit['commit'])
        branch['trail'] = trail

    # We create a unique list of commits
    unique_commmits = []
    hash_dict = {}
    for branch in branches_data:
        for commit in branch['commits']:
            if commit['commit'] not in hash_dict:
                unique_commmits.append(commit)
                hash_dict[commit['commit']] = commit['commit']


    pp.pprint(unique_commmits)
    pp.pprint(hash_dict)

    pp.pprint(branches_data)
    pp.pprint(diff_list)
    return

def get_archive_folder_path(project_info):
    folder = project_info['git']['project']['tmp_directory']
    archive = project_info['git']['project']['archive']
    return os.path.join(folder, archive)

def get_git_project_folder_path(project_info):
    folder = project_info['git']['project']['tmp_directory']
    archive = project_info['git']['project']['archive']
    git_name = project_info['git']['project']['name']
    return os.path.join(folder, archive, 'project', git_name)

def is_project_folder_present(project_info):
    """ Checks if the folder structure exists """
    folder_path = get_archive_folder_path(project_info)
    if not os.path.exists(folder_path):
        return False
    return True

def is_git_project_folder_present(project_info):
    """ Checks if the folder structure exists """
    folder_path = get_archive_folder_path(project_info)
    if not os.path.exists(os.path.join(folder_path, 'project')):
        return False
    return True

def is_log_project_folder_present(project_info):
    """ Checks if the folder structure exists """
    folder_path = get_archive_folder_path(project_info)
    if not os.path.exists(os.path.join(folder_path, 'log')):
        return False
    return True


def create_tmp_folder_for_git_project(project_info):
    """ Creates git rpoject folder structure """
    folder_path = get_archive_folder_path(project_info)
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)

    os.makedirs(os.path.join(folder_path, 'project'))
    os.makedirs(os.path.join(folder_path, 'log'))

def clear_logs_folder(project_folder_path):
    """ Remove and re-creates the logs folder """
    logs_path = os.path.join(project_folder_path, 'log')
    if os.path.exists(logs_path):
        shutil.rmtree(logs_path)
    os.makedirs(logs_path)

def execute_command_list(command_list, project_directory, project_cwd, out_file_path, err_file_path):
    """ Executes a list of commands, if the command fails it returns inmediately """
    reports = {}
    reports['status'] = True
    reports['commands'] = []

    for command in command_list:
        clear_logs_folder(project_directory)
        file_stdout = open(out_file_path, 'w')
        file_stderr = open(err_file_path, 'w')

        report = {}

        try:
            subprocess.check_call(
                command,
                stdout=file_stdout,
                stderr=file_stderr,
                cwd=project_cwd
            )
        except subprocess.CalledProcessError:
            reports['status'] = False
            report['status'] = 'ERROR'
        else:
            report['status'] = 'OK'

        file_stdout.close()
        file_stderr.close()

        file_stdout = open(out_file_path, 'r')
        file_stderr = open(err_file_path, 'r')

        report['command'] = command
        report['out'] = file_stdout.read()
        report['err'] = file_stderr.read()

        reports['commands'].append(report)

        file_stdout.close()
        file_stderr.close()

        if not reports['status']:
            break

    return reports

def commands_clone_git_project(project_info):
    """ clone a git repo """
    folder_path = get_archive_folder_path(project_info)
    project_cwd = os.path.join(folder_path, 'project')
    stdout_path = os.path.join(folder_path, 'log', 'git_clone_stdout.txt')
    stderr_path = os.path.join(folder_path, 'log', 'git_clone_stderr.txt')

    reports = execute_command_list(project_info['git']['clone']['commands'], str(folder_path), project_cwd, stdout_path, stderr_path)
    return reports

def commands_fetch_git_project(project_info):
    """ fetch a git repo """
    folder_path = get_archive_folder_path(project_info)
    project_cwd = get_git_project_folder_path(project_info)
    stdout_path = os.path.join(folder_path, 'log', 'git_clone_stdout.txt')
    stderr_path = os.path.join(folder_path, 'log', 'git_clone_stderr.txt')

    reports = execute_command_list(project_info['git']['fetch']['commands'], str(folder_path), project_cwd, stdout_path, stderr_path)
    return reports

def commands_get_remote_branch_names(project_info):
    """ Returns all remote branches names """
    folder_path = get_archive_folder_path(project_info)
    project_cwd = get_git_project_folder_path(project_info)
    stdout_path = os.path.join(folder_path, 'log', 'git_clone_stdout.txt')
    stderr_path = os.path.join(folder_path, 'log', 'git_clone_stderr.txt')

    command = ['git', 'branch', '-r']
    commands = []
    commands.append(command)
    reports = execute_command_list(commands, str(folder_path), project_cwd, stdout_path, stderr_path)
    return reports

def extract_remote_branch_names_from_reports(reports):
    remote_branch_names = []

    if not reports['status']:
        return []

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


def commands_get_branch_names(project_info):
    """ Returns all local branches """
    folder_path = get_archive_folder_path(project_info)
    project_cwd = get_git_project_folder_path(project_info)
    stdout_path = os.path.join(folder_path, 'log', 'git_clone_stdout.txt')
    stderr_path = os.path.join(folder_path, 'log', 'git_clone_stderr.txt')

    command = ['git', 'branch']
    commands = []
    commands.append(command)
    reports = execute_command_list(commands, str(folder_path), project_cwd, stdout_path, stderr_path)
    return reports

def extract_branch_names_from_report(reports):
    """ Extract a list of names from the raw branch info """
    branch_names = []

    if not reports['status']:
        return []

    for command in reports['commands']:
        if command['command'] == ['git', 'branch'] and command['status'] == 'OK':
            names = command['out'].split('\n')
            for name in names:
                name = name.replace('*', '')
                name = name.strip()
                if len(name) > 0:
                    branch_names.append(name)
    return branch_names

def checkout_remote_branches_to_local(project_info, remote_branch_names):
    """ Check out all the remote branches to local ones """
    folder_path = get_archive_folder_path(project_info)
    project_cwd = get_git_project_folder_path(project_info)
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
    reports = execute_command_list(commands, str(folder_path), project_cwd, stdout_path, stderr_path)
    return reports

def commands_get_branch_names_and_hashes(project_info, branch_names):
    """ Fetch the hash of every branch name """
    folder_path = get_archive_folder_path(project_info)
    project_cwd = get_git_project_folder_path(project_info)
    stdout_path = os.path.join(folder_path, 'log', 'git_clone_stdout.txt')
    stderr_path = os.path.join(folder_path, 'log', 'git_clone_stderr.txt')

    commands = []

    for name in branch_names:
        commands.append(['git', 'rev-parse', name])

    reports = execute_command_list(commands, str(folder_path), project_cwd, stdout_path, stderr_path)
    return reports

def extract_branch_names_and_hashes_from_report(reports):
    branch_names = []

    if not reports['status']:
        return []

    for command in reports['commands']:
        if command['command'][0] == 'git' and command['command'][1] == 'rev-parse' and command['status'] == 'OK':
            branch = {}
            branch['name'] = command['command'][2].strip()
            branch['hash'] = command['out'].strip()
            branch_names.append(branch)
    return branch_names

def commands_get_commits_from_branch(project_info, branch_name, branch_hash):
    """ Get all commits from a branch, only first parent """
    folder_path = get_archive_folder_path(project_info)
    project_cwd = get_git_project_folder_path(project_info)
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

    reports = execute_command_list(commands, str(folder_path), project_cwd, stdout_path, stderr_path)
    return reports

def extract_and_format_commits_from_report(reports):
    commits = []

    if not reports['status']:
        return []

    for command in reports['commands']:
        if command['command'][0] == 'git' and command['command'][1] == 'log' and command['status'] == 'OK':
            commits_string = '[' + command['out'][:-1] + ']'
            commits_obj = json.loads(commits_string)

            for commit in commits_obj:
                commit['parent_hashes'] = commit['parent_hashes'].split(' ')
            commits = commits_obj
    return commits

def trim_commit_list_with_known_branches(commits, known_branches):
    trimmed_commits = []

    for commit in commits:
        trimmed_commits.append(commit)
        for branch in known_branches:
            if commit['hash'] == branch['hash']:
                return trimmed_commits
    return trimmed_commits

def commands_get_shared_commit_between_branches(project_info, branch1, branch2):
    """ Get the common ancestor commit between two branches """
    folder_path = get_archive_folder_path(project_info)
    project_cwd = get_git_project_folder_path(project_info)
    stdout_path = os.path.join(folder_path, 'log', 'git_clone_stdout.txt')
    stderr_path = os.path.join(folder_path, 'log', 'git_clone_stderr.txt')

    command = ['git', 'merge-base', branch1['hash'], branch2['hash']]

    reports = execute_command_list([command], str(folder_path), project_cwd, stdout_path, stderr_path)
    return reports

def extract_shared_commit_hash(reports):
    if not reports['status']:
        return []

    for command in reports['commands']:
        if command['command'][0] == 'git' and command['command'][1] == 'merge-base' and command['status'] == 'OK':
            return command['out'].strip()

    return ''

def get_merge_target_from_branch_list(branch, branch_list, known_branches):
    """ Returns merge target branch for a given branch. If not found on known branches, it returns 'master' or itself """
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

def get_fork_point_between_branches(branch_target, branch_origin):
    for commit_origin in branch_origin['commits']:
        for commit_target in branch_target['commits']:
            if commit_origin['hash'] == commit_target['hash']:
                return commit_origin['hash']
    return ''


def commands_get_diff_between_commits(project_info, commit_hash_1, commit_hash_2):
    """ Get the diff between 2 commits """

    folder_path = get_archive_folder_path(project_info)
    project_cwd = get_git_project_folder_path(project_info)
    stdout_path = os.path.join(folder_path, 'log', 'git_clone_stdout.txt')
    stderr_path = os.path.join(folder_path, 'log', 'git_clone_stderr.txt')

    command = ['git', 'diff', commit_hash_1, commit_hash_2]

    reports = execute_command_list([command], str(folder_path), project_cwd, stdout_path, stderr_path)
    return reports

def extract_diff_from_report(reports):
    """ We extract the content of the diff from the report """
    commits = []

    if not reports['status']:
        return []

    for command in reports['commands']:
        if command['command'][0] == 'git' and command['command'][1] == 'diff' and command['status'] == 'OK':
            return command['out']

    return ''


def main():

    branch1 = {}
    branch1['name'] = 'master'
    branch1['hash'] = '50a284b3d0c7d95d4e8ea99acbfb9898765ce4c6'
    branch1['merge_target'] = {}
    branch1['merge_target']['name'] = 'master'
    branch1['merge_target']['hash'] = '50a284b3d0c7d95d4e8ea99acbfb9898765ce4c6'

    branch2 = {}
    branch2['name'] = 'branch-1'
    branch2['hash'] = 'f486ee42b56432375f47b206a4281fd9ad0de02e'
    branch2['merge_target'] = {}
    branch2['merge_target']['name'] = 'master'
    branch2['merge_target']['hash'] = '50a284b3d0c7d95d4e8ea99acbfb9898765ce4c6'

    branch3 = {}
    branch3['name'] = 'name-3'
    branch3['hash'] = '0000100001000010000100001000010000100001'
    branch3['merge_target'] = {}
    branch3['merge_target']['name'] = 'name-1'
    branch3['merge_target']['hash'] = '0000100001000010000100001000010000100001'

    obj = {}
    obj['git'] = {}
    obj['git']['project'] = {}
    obj['git']['project']['tmp_directory'] = '../target_folder'
    obj['git']['project']['archive'] = 'proj-28-0123ABC'
    obj['git']['project']['name'] = 'test-repo'
    obj['git']['project']['url'] = 'https://llorensmarti@bitbucket.org/llorensmarti/test-repo.git'
    obj['git']['branch'] = {}
    obj['git']['branch']['known'] = []
    # obj['git']['branch']['known'].append(branch1)
    # obj['git']['branch']['known'].append(branch2)
    # obj['git']['branch']['known'].append(branch3)
    obj['git']['branch']['commands'] = []
    obj['git']['branch']['commands'].append(['coomand-1','arg1','arg2'])
    obj['git']['clone'] = {}
    obj['git']['clone']['commands'] = []
    obj['git']['clone']['commands'].append(['git', 'clone', 'https://llorensmarti@bitbucket.org/llorensmarti/test-repo.git'])
    obj['git']['fetch'] = {}
    obj['git']['fetch']['commands'] = []
    obj['git']['fetch']['commands'].append(['git', 'checkout', 'master'])
    obj['git']['fetch']['commands'].append(['git', 'reset', '--hard', 'origin/master'])
    obj['git']['fetch']['commands'].append(['git', 'clean', '-f', '-d', '-q'])
    obj['git']['fetch']['commands'].append(['git', 'pull', '-r', 'origin', 'master'])
    obj['git']['fetch']['commands'].append(['git', 'checkout', 'master'])
    obj['git']['fetch']['commands'].append(['git', 'submodule', 'sync'])
    obj['git']['fetch']['commands'].append(['git', 'submodule', 'update', '--init', '--recursive'])

    ret = fetch_git_project(obj)

    print ret

if __name__ == '__main__':
    main()