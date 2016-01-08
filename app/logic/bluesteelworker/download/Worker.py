""" Worker code """

# Disable warning for relative imports
# pylint: disable=W0403

from CommandExecutioner import CommandExecutioner
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


def get_cwd():
    return os.path.dirname(os.path.abspath(__file__))

def fragment_layout_in_project_infos(layout, tmp_path):
    """ Fragment a layout objects on individual project objects """
    project_to_feed = layout['project_index_path']
    projects = []
    for index, project in enumerate(layout['projects']):

        ppi = pprint.PrettyPrinter(depth=10)
        ppi.pprint(project)

        obj = {}
        obj['feed'] = {}
        obj['feed']['url'] = project['feed_url']
        obj['feed']['active'] = index == project_to_feed
        obj['git'] = {}
        obj['git']['project'] = {}
        obj['git']['project']['current_working_directory'] = get_cwd()
        obj['git']['project']['tmp_directory'] = tmp_path
        obj['git']['project']['archive'] = layout['uuid']
        obj['git']['project']['name'] = project['uuid']
        obj['git']['branch'] = {}
        obj['git']['branch']['known'] = project['git_project']['branches']

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
        settings_obj['entry_point'] = 'http://www.test.com/settings/not/available/'
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

def get_bootstrap_urls(entry_point_url, session):
    """ Gets all the important urls from Bluesteel """
    resp = session.get(entry_point_url, {})

    if resp['succeed'] and resp['content']['status'] == 200:
        return resp['content']['data']
    else:
        bootstrap_urls = {}
        bootstrap_urls['layouts_url'] = 'http://url/not/available/'
        bootstrap_urls['worker_info_url'] = 'http://url/not/available/'
        bootstrap_urls['create_worker_url'] = 'http://url/not/available/'
        bootstrap_urls['login_worker_url'] = 'http://url/not/available/'
        return bootstrap_urls

def process_get_or_create_worker(bootstrap_urls, host_info, session):
    """ Gets or create a Worker, returns worker info """
    url = '{0}{1}/'.format(bootstrap_urls['worker_info_url'], host_info['uuid'])
    resp = session.get(url, {})

    if resp['content']['status'] == 400:
        print '- Creating Worker'
        resp = session.post(bootstrap_urls['create_worker_url'], {}, json.dumps(host_info))

    connection_info = {}
    connection_info['succeed'] = resp['content']['status'] == 200
    connection_info['worker'] = resp['content']['data']['worker']
    return connection_info

def process_connect_worker(bootstrap_urls, worker_info, session):
    """ Make woerker login to BlueSteel """
    print '- Login Worker'

    login_info = {}
    login_info['username'] = worker_info['uuid'][0:30]
    login_info['password'] = worker_info['uuid']

    resp = session.post(bootstrap_urls['login_worker_url'], {}, json.dumps(login_info))

    connection_info = {}
    connection_info['git_feeder'] = worker_info['git_feeder']
    connection_info['succeed'] = resp['content']['status'] == 200
    return connection_info

def extract_projects_from_layouts(bootstrap_urls, settings, session):
    """ Read layouts from Bluesteel and return all the projects availables """
    process_info = {}
    process_info['succeed'] = True
    process_info['projects'] = []

    print '- Getting layout list'
    resp = session.get(bootstrap_urls['layouts_url'], {})
    if resp['succeed'] == False:
        process_info['succeed'] = False
        return process_info

    for layout_url in resp['content']['data']['layouts']:
        print '- Get layout'
        resp = session.get(layout_url, {})
        if resp['succeed'] == False:
            process_info['succeed'] = False
            return process_info

        layout = resp['content']['data']

        if not layout['active']:
            print 'Layout not active!'
            continue

        print '- Fragmenting layout'
        project_fragments = fragment_layout_in_project_infos(layout, settings['tmp_path'])

        for project in project_fragments:
            process_info['projects'].append(project)

    return process_info


def process_git_fetch_and_feed(bootstrap_urls, settings, session, feed):
    """ Fetch all layouts and feed them to BlueSteel """
    process_info = {}
    process_info['succeed'] = True

    res = extract_projects_from_layouts(bootstrap_urls, settings, session)
    if not res['succeed']:
        process_info['succeed'] = False
        return process_info

    for project in res['projects']:
        print '- Fetching git project'
        fetcher = GitFetcher.GitFetcher()
        fetcher.fetch_git_project(project)

        # ppi = pprint.PrettyPrinter(depth=10)
        # ppi.pprint(fetcher.feed_data)

        obj_json = json.dumps(fetcher.feed_data)

        # print project['feed']['url']

        if project['feed']['active'] and feed:
            print '- Feeding git project'
            resp = session.post(project['feed']['url'], {}, obj_json)
            if not resp['succeed']:
                process_info = resp
                return process_info

            # ppi.pprint(resp)

    print '- Finshed fetching and feeding'
    return process_info

def process_get_available_benchmark_execution(bootstrap_urls, session):
    """ Will access Bluesteel to acquire the next available benchmark execution """
    print '- Getting benchmark execution'

    resp = session.post(bootstrap_urls['acquire_benchmark_execution_url'], {}, '')
    if resp['succeed'] == False:
        print '    - An error occurred:'
        print resp
        return None

    if resp['content']['status'] != 200:
        print '- Get available benchmark failed'
        return None

    data = resp['content']['data']
    return data
    # for command in data['definition']['command_set']['commands']:
    #     print '------> ', command['command']


def process_get_and_execute_task(bootstrap_urls, settings, session):
    """ It request a benchmark execution and executes it, it returns a report from that """
    bench_exec = process_get_available_benchmark_execution(bootstrap_urls, session)

    if not bench_exec:
        return

    commands = []
    for command in bench_exec['definition']['command_set']['commands']:
        commands.append(command['command'])

    layout_uuid = bench_exec['definition']['layout']['uuid']
    project_uuid = bench_exec['definition']['project']['uuid']

    tmp_path_list = settings['tmp_path'][:]
    tmp_path_list.append('bench_exec')

    project_cwd_list = settings['tmp_path'][:]
    project_cwd_list.append(layout_uuid)
    project_cwd_list.append(project_uuid)

    tmp_path = reduce(os.path.join, tmp_path_list)
    project_cwd = reduce(os.path.join, project_cwd_list)

    print '++ commands: ', commands
    print '++ layout: ', layout_uuid
    print '++ project: ', project_uuid
    print '++ project cwd: ', project_cwd

    res = CommandExecutioner.execute_command_list(commands, tmp_path, project_cwd)
    print '!!--- ', res

    return res


def main():
    """ Main """
    ppi = pprint.PrettyPrinter(depth=10)

    settings = read_settings()
    ppi.pprint(settings)

    host_info = get_host_info()
    session = Request.Session()

    bootstrap_urls = get_bootstrap_urls(settings['entry_point'], session)
    ppi.pprint(bootstrap_urls)


    while True:
        worker_info = process_get_or_create_worker(bootstrap_urls, host_info, session)
        if worker_info['succeed'] == False:
            continue

        con_info = process_connect_worker(bootstrap_urls, worker_info['worker'], session)
        if con_info['succeed'] == False:
            continue

        session.post(worker_info['worker']['url']['update_activity_point'], {}, '')

        ppi.pprint(worker_info)
        ppi.pprint(con_info)
        time.sleep(1)

        if con_info['succeed']:
            working = True
            while working:
                process_git_fetch_and_feed(
                    bootstrap_urls,
                    settings,
                    session,
                    con_info['git_feeder'])

                process_get_and_execute_task(bootstrap_urls, settings, session)


                time.sleep(1000)



if __name__ == '__main__':
    main()
