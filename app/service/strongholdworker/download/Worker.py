""" Worker code """

# Disable warning for relative imports
# pylint: disable=W0403

import GitFetcher
import Request
import os
import time
import json
import pprint
import uuid
import socket
import platform


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


def fragment_layout_in_project_infos(layout, tmp_path):
    """ Fragment a layout objects on individual project objects """
    projects = []
    for project in layout['projects']:
        obj = {}
        obj['feed'] = {}
        obj['feed']['url'] = project['feed_url']
        obj['git'] = {}
        obj['git']['project'] = {}
        obj['git']['project']['current_working_directory'] = os.path.dirname(os.path.abspath(__file__))
        obj['git']['project']['tmp_directory'] = tmp_path
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

def read_settings():
    """ Reads and return an objects with settings """
    settings_file = open('settings.json')
    settings_obj = {}
    try:
        settings_obj = json.loads(settings_file.read())
    except ValueError, error:
        print error
        settings_obj['tmp_path'] = ['tmp']
        settings_obj['entry_point'] = 'http://www.test.com'
    settings_file.close()
    return settings_obj

def get_host_info():
    """ Returns an object with unique information about the host """
    obj = {}
    # uuid.getnode() can return a random number, we need to fix it
    obj['uuid'] = str(uuid.uuid3(uuid.NAMESPACE_DNS, str(uuid.getnode())))
    obj['host_name'] = socket.gethostname()
    obj['operative_system'] = '{0}-{1}'.format(
        platform.system(),
        platform.release()
    )
    return obj

def process_connect_worker(settings, host_info, session):
    """ Create a Worker if first time and make login to BlueSteel """
    connection_info = {}

    url = '{0}{1}/'.format(settings['worker_info_point'], host_info['uuid'])
    resp = session.get(url, {})

    if resp['content']['status'] == 400:
        print '- Creating Worker'
        resp = session.post(settings['create_worker_info_point'], {}, json.dumps(host_info))

    login_info = {}
    login_info['username'] = host_info['uuid'][0:30]
    login_info['password'] = host_info['uuid']

    print '- Login Worker'
    resp = session.post(settings['login_worker_point'], {}, json.dumps(login_info))

    connection_info['git_feeder'] = True
    connection_info['succeed'] = resp['content']['status'] == 200
    return connection_info

def process_git_feed(settings, session):
    """ Fetch all layouts and feed them to BlueSteel """
    process_info = {}
    process_info['succeed'] = True

    print '- Getting layout list'
    resp = session.get(settings['entry_point'], {})
    if resp['succeed'] == False:
        process_info['succeed'] = False
        return process_info

    for layout_url in resp['content']['data']['layouts']:
        print '- Get layout'
        resp = session.get(layout_url, {})
        if resp['succeed'] == False:
            process_info['succeed'] = False
            return process_info

        print '- Fragmenting layout'
        projects = fragment_layout_in_project_infos(resp['content']['data'], settings['tmp_path'])

        for project in projects:
            fetcher = GitFetcher.GitFetcher()

            print '- Fetching git project'
            fetcher.fetch_git_project(project)

            ppi = pprint.PrettyPrinter(depth=10)
            ppi.pprint(fetcher.feed_data)

            obj_json = json.dumps(fetcher.feed_data)

            print project['feed']['url']

            print '- Feeding git project'
            resp = session.post(project['feed']['url'], {}, obj_json)
            if resp['succeed'] == False:
                process_info['succeed'] = False
                return process_info

            ppi.pprint(resp)

    print '- Finshed feeding'
    return process_info


def main():
    """ Main """
    # ppi = pprint.PrettyPrinter(depth=10)

    settings = read_settings()
    host_info = get_host_info()
    session = Request.Session()


    while True:
        con_info = process_connect_worker(settings, host_info, session)

        if con_info['succeed']:

            working = True
            while working:
                if con_info['git_feeder']:
                    print '- Start git feeding'
                    resp = process_git_feed(settings, session)

                working = resp['succeed']
                time.sleep(3)



if __name__ == '__main__':
    main()
