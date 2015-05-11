""" Worker code """

# Disable warning for relative imports
# pylint: disable=W0403

import GitFetcher
import pprint

def main():
    """ Main """
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
    obj['git']['branch']['commands'].append(['coomand-1', 'arg1', 'arg2'])
    obj['git']['clone'] = {}
    obj['git']['clone']['commands'] = []
    obj['git']['clone']['commands'].append(
        ['git', 'clone', 'https://llorensmarti@bitbucket.org/llorensmarti/test-repo.git']
    )
    obj['git']['fetch'] = {}
    obj['git']['fetch']['commands'] = []
    obj['git']['fetch']['commands'].append(['git', 'checkout', 'master'])
    obj['git']['fetch']['commands'].append(['git', 'reset', '--hard', 'origin/master'])
    obj['git']['fetch']['commands'].append(['git', 'clean', '-f', '-d', '-q'])
    obj['git']['fetch']['commands'].append(['git', 'pull', '-r', 'origin', 'master'])
    obj['git']['fetch']['commands'].append(['git', 'checkout', 'master'])
    obj['git']['fetch']['commands'].append(['git', 'submodule', 'sync'])
    obj['git']['fetch']['commands'].append(['git', 'submodule', 'update', '--init', '--recursive'])

    fetcher = GitFetcher.GitFetcher()
    fetcher.fetch_git_project(obj)

    ppi = pprint.PrettyPrinter(depth=6)
    ppi.pprint(fetcher.feed_data)


if __name__ == '__main__':
    main()
