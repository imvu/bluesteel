""" Worker code """

# Disable warning for relative imports
# pylint: disable=W0403

import GitFetcher
import os
import time
import json
import pprint
import urllib2

def get_obj():
    """ Returns a predefined object with fetch info """
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
    obj['git']['project']['current_working_directory'] = os.path.dirname(__file__)
    obj['git']['project']['tmp_directory'] = 'tmp'
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
    return obj

def command_string_to_vector(command):
    return command.split()

def fragment_layout_in_project_infos(layout):
    """ Fragment a layout objects on individual project objects """
    projects = []
    for project in layout['projects']:
        obj = {}
        obj['git'] = {}
        obj['git']['project'] = {}
        obj['git']['project']['current_working_directory'] = os.path.dirname(os.path.abspath(__file__))
        obj['git']['project']['tmp_directory'] = 'tmp'
        obj['git']['project']['archive'] = layout['archive']
        obj['git']['project']['name'] = layout['name']
        obj['git']['branch'] = {}
        obj['git']['branch']['known'] = []

        for command_set in project['command_group']['command_sets']:
            set_name = command_set['name'].lower()

            if set_name == 'clone':
                obj['git']['clone'] = {}
                obj['git']['clone']['commands'] = []
                for command in command_set['commands']:
                    obj['git']['clone']['commands'].append(command_string_to_vector(command['command']))

            if set_name == 'fetch':
                obj['git']['fetch'] = {}
                obj['git']['fetch']['commands'] = []
                for command in command_set['commands']:
                    obj['git']['fetch']['commands'].append(command_string_to_vector(command['command']))

        projects.append(obj)
    return projects

def main():
    """ Main """
    bluesteel_url = 'http://localhost:28028/bluesteel/layout/all/urls/'

    # password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm() # seriously?
    # password_manager.add_password(None, github_url, 'user', '***')

    # auth = urllib2.HTTPBasicAuthHandler(password_manager) # create an authentication handler
    # opener = urllib2.build_opener(auth) # create an opener with the authentication handler
    # urllib2.install_opener(opener) # install the opener...
    ppi = pprint.PrettyPrinter(depth=10)

    while True:
        print 'Making request'

        request = urllib2.Request(bluesteel_url) # Manual encoding required
        handler = urllib2.urlopen(request)
        resp_json = handler.read()
        resp = json.loads(resp_json)

        # ppi.pprint(resp)
        for layout_url in resp['data']['layouts']:

            ppi.pprint(layout_url)
            request = urllib2.Request(layout_url) # Manual encoding required
            handler = urllib2.urlopen(request)
            resp_json = handler.read()
            resp = json.loads(resp_json)

            ppi.pprint(resp)

            projects = fragment_layout_in_project_infos(resp['data'])

            ppi.pprint(projects)
            for project in projects:
                fetcher = GitFetcher.GitFetcher()
                fetcher.fetch_git_project(project)
                ppi.pprint(fetcher.feed_data)
                ppi.pprint(fetcher.report_stack)

            time.sleep(30)



if __name__ == '__main__':
    main()
