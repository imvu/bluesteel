""" Feeder test helper functions """

def hash_string(commit_hash_num):
    return str('{0:05d}'.format(commit_hash_num) * 8)

def create_commit(commit_hash_num, parents, author_name, email, create_date, commit_date):
    """ Creates a commit object representation """
    commit = {}
    commit['hash'] = hash_string(commit_hash_num)
    commit['parent_hashes'] = parents
    commit['author'] = {}
    commit['author']['name'] = author_name
    commit['author']['email'] = email
    commit['author']['date'] = create_date
    commit['committer'] = {}
    commit['committer']['name'] = author_name
    commit['committer']['email'] = email
    commit['committer']['date'] = commit_date
    return commit

def create_diff(commit_hash_son, commit_hash_parent, content):
    """ Creates a diff object representation """
    diff = {}
    diff['commit_hash_son'] = commit_hash_son
    diff['commit_hash_parent'] = commit_hash_parent
    diff['content'] = content
    return diff

def create_branch(name, commit_hash_num, trail, merge_target):
    """ Creates a branch object representation """
    branch = {}
    branch['branch_name'] = name
    branch['commit_hash'] = hash_string(commit_hash_num)
    branch['trail'] = trail
    branch['merge_target'] = merge_target
    return branch

def create_merge_target(current_name, current_hash, target_name, target_hash, fork_point, content):
    """ Creates a merge target object representation """
    merge_target = {}
    merge_target['current_branch'] = {}
    merge_target['current_branch']['name'] = current_name
    merge_target['current_branch']['commit_hash'] = current_hash
    merge_target['target_branch'] = {}
    merge_target['target_branch']['name'] = target_name
    merge_target['target_branch']['commit_hash'] = target_hash
    merge_target['fork_point'] = fork_point
    merge_target['diff'] = {}
    merge_target['diff']['commit_hash_son'] = current_hash
    merge_target['diff']['commit_hash_parent'] = fork_point
    merge_target['diff']['content'] = content
    return merge_target

def create_feed_data_and_report(feed_data, reports):
    obj = {}
    obj['feed_data'] = feed_data
    obj['reports'] = reports
    return obj

def get_default_report():
    """ Returns a default correct report """
    reports = []

    report = {}
    report['commands'] = []

    command = {}
    command['command'] = ['command1', 'arg1', 'arg2']
    command['result'] = {}
    command['result']['error'] = 'default-error'
    command['result']['out'] = 'default-out'
    command['result']['status'] = 0

    report['commands'].append(command)
    reports.append(report)
    return reports
