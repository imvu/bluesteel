""" Feeder test helper functions """

def hash_string(commit_hash_num):
    return '{0:05d}'.format(commit_hash_num) * 8

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

def create_merge_target(target_name, commit_son, commit_parent, content):
    """ Creates a merge target object representation """
    target_merge = {}
    target_merge['target_branch_name'] = target_name
    target_merge['diff'] = {}
    target_merge['diff']['commit_hash_son'] = commit_son
    target_merge['diff']['commit_hash_parent'] = commit_parent
    target_merge['diff']['content'] = content
    return target_merge
