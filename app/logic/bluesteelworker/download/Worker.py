""" Worker code """

# Disable warning for relative imports
# pylint: disable=W0403

from CommandExecutioner import CommandExecutioner
from ProjectFolderManager import ProjectFolderManager
import logging as log
import GitFetcher
import Request
import os
import json
import uuid
import socket
import platform
# import time
# import pprint

def command_string_to_vector(command):
    return command.split()

def get_cwd():
    return os.path.dirname(os.path.abspath(__file__))

def fragment_layout_in_project_infos(layout, tmp_path):
    """ Fragment a layout objects on individual project objects """
    project_to_feed = layout['project_index_path']
    projects = []
    for index, project in enumerate(layout['projects']):

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
        obj['git']['project']['git_project_search_path'] = project['git_project_folder_search_path']
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
        fetcher = GitFetcher.GitFetcher(log.DEBUG)
        fetcher.fetch_git_project(project)

        obj_json = json.dumps(fetcher.feed_data)

        if project['feed']['active'] and feed:
            print '- Feeding git project'
            resp = session.post(project['feed']['url'], {}, obj_json)
            # ppi.pprint(resp)
            if not resp['succeed']:
                print '- Error occurred while feeding project'
                process_info = resp
                return process_info

    print '- Finshed fetching and feeding'
    return process_info

def process_get_available_benchmark_execution(bootstrap_urls, session):
    """ Will access Bluesteel to acquire the next available benchmark execution """
    print '- Getting benchmark execution'

    resp = session.post(bootstrap_urls['acquire_benchmark_execution_url'], {}, '')
    if resp['succeed'] == False:
        # print '    - An error occurred:'
        # print resp
        return None

    if resp['content']['status'] != 200:
        print '- Get available benchmark failed'
        return None

    data = resp['content']['data']
    return data

def process_execute_task(settings, benchmark_execution):
    """ It executes a benchmark execution, it returns a report from that """

    commands = []
    for command in benchmark_execution['definition']['command_set']['commands']:
        commands.append(command['command'])

    layout_uuid = benchmark_execution['definition']['layout']['uuid']
    project_uuid = benchmark_execution['definition']['project']['uuid']
    local_search_path = benchmark_execution['definition']['project']['git_project_folder_search_path']

    paths = ProjectFolderManager.get_folder_paths(
        get_cwd(),
        settings['tmp_path'][:],
        layout_uuid,
        project_uuid,
        local_search_path
    )

    git_path = ProjectFolderManager.get_cwd_of_first_git_project_found_in(paths['project'])

    res = CommandExecutioner.execute_command_list(
        commands,
        paths['log'],
        git_path,
        False)

    return res

def prepare_results_before_feed(results):
    """ Reads the output of all the executed commands and prepares the info to feed """
    ret = {}
    ret['command_set'] = []

    for index, command in enumerate(results['commands']):
        obj = {}
        obj['command'] = command['command']
        obj['result'] = {}
        obj['result']['status'] = command['result'].get('status', 0)
        obj['result']['error'] = command['result'].get('error', '')
        obj['result']['start_time'] = command['result']['start_time']
        obj['result']['finish_time'] = command['result']['finish_time']

        out_json = []

        try:
            out_json = json.loads(command['result'].get('out', '[]'))
        except ValueError as error:
            res = {}
            res['id'] = 'error-{0}'.format(index)
            res['visual_type'] = 'text'
            res['data'] = '{0}\n{1}'.format(
                str(error),
                command['result']['out'])
            out_json.append(res)
        except KeyError as error:
            res = {}
            res['id'] = 'error-{0}'.format(index)
            res['visual_type'] = 'text'
            res['data'] = '{0}\n{1}'.format(
                str(error),
                command['result']['out'])
            out_json.append(res)

        if not isinstance(out_json, list):
            out_json = [out_json]

        obj['result']['out'] = out_json
        ret['command_set'].append(obj)
    return ret


def process_feed_benchmark_execution_results(session, results, bench_exec):
    """ Takes the results of the executed commands and feed them to BlueSteel """
    results_to_feed = prepare_results_before_feed(results)

    json_res = json.dumps(results_to_feed)

    resp = session.post(bench_exec['url']['save'], {}, json_res)
    return resp


def main():
    """ Main """
    settings = read_settings()
    host_info = get_host_info()
    session = Request.Session()

    bootstrap_urls = get_bootstrap_urls(settings['entry_point'], session)

    while True:
        print '+ get or create worker.'
        worker_info = process_get_or_create_worker(bootstrap_urls, host_info, session)
        if worker_info['succeed'] == False:
            continue

        print '+ connect worker.'
        con_info = process_connect_worker(bootstrap_urls, worker_info['worker'], session)
        if con_info['succeed'] == False:
            continue

        print '+ update worker activity.'
        session.post(worker_info['worker']['url']['update_activity_point'], {}, '')

        if con_info['succeed']:
            working = True
            while working:

                print '+ fetch and feed gir project.'
                process_git_fetch_and_feed(
                    bootstrap_urls,
                    settings,
                    session,
                    con_info['git_feeder'])

                print '+ get available benchmarks.'
                bench_exec = process_get_available_benchmark_execution(bootstrap_urls, session)

                if not bench_exec:
                    continue

                print '+ execute benchmark.'
                res = process_execute_task(settings, bench_exec)

                print '+ save benchmark results.'
                process_feed_benchmark_execution_results(
                    session,
                    res,
                    bench_exec)


if __name__ == '__main__':
    main()
