""" Feeder test helper functions """

def hash_string(commit_hash_num):
    return '{0:05d}'.format(commit_hash_num) * 8

def create_commit(commit_hash_num, parents, author_name, email, create_date, commit_date):
    """ Creates a commit objecte representation """
    commit = {}
    commit['commit_hash'] = hash_string(commit_hash_num)
    commit['commit_parents'] = parents
    commit['date_creation'] = create_date
    commit['date_commit'] = commit_date
    commit['user'] = {}
    commit['user']['name'] = author_name
    commit['user']['email'] = email
    return commit

def create_branch(name, commit_hash_num, trail, merge_target):
    """ Creates a branch objecte representation """
    branch = {}
    branch['branch_name'] = name
    branch['commit_hash'] = hash_string(commit_hash_num)
    branch['trail'] = trail
    branch['merge_target'] = merge_target
    return branch

def create_merge_target(target_name, commit_son, commit_parent, content):
    """ Creates a merge target objecte representation """
    target_merge = {}
    target_merge['target_branch_name'] = target_name
    target_merge['diff'] = {}
    target_merge['diff']['commit_hash_son'] = commit_son
    target_merge['diff']['commit_hash_parent'] = commit_parent
    target_merge['diff']['content'] = content
    return target_merge
