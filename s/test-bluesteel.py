#!/usr/bin/env python

import subprocess
import errno
import sys
import os

def get_red_string(string):
    return '\033[91m' + string + '\033[0m'

def get_green_string(string):
    return '\033[92m' + string + '\033[0m'

def get_packed_app_info(tags, path):
    obj = {}
    obj['tags'] = tags
    obj['path'] = path
    return obj

def get_test_list():
    """ Returns a list of tests, every test its a list of commands """

    packs = []
    packs.append(get_packed_app_info(['app', 'gitrepo'],            'app/logic/gitrepo',))
    packs.append(get_packed_app_info(['app', 'gitfeeder'],          'app/logic/gitfeeder',))
    packs.append(get_packed_app_info(['app', 'bluesteelworker'],    'app/logic/bluesteelworker',))
    packs.append(get_packed_app_info(['app', 'bluesteel'],          'app/logic/bluesteel',))
    packs.append(get_packed_app_info(['app', 'benchmark'],          'app/logic/benchmark',))
    packs.append(get_packed_app_info(['app', 'httpcommon'],         'app/logic/httpcommon',))
    packs.append(get_packed_app_info(['app', 'commandrepo'],        'app/logic/commandrepo',))
    packs.append(get_packed_app_info(['app', 'logger'],             'app/logic/logger',))
    packs.append(get_packed_app_info(['app', 'mailing'],            'app/logic/mailing',))
    packs.append(get_packed_app_info(['app', 'presenter'],          'app/presenter',))

    test_list = []
    test_list.append((['python'], ['s/internal/test-python.py']))
    test_list.append((['hooks'], ['python', 's/internal/install-hooks.py']))
    test_list.append((['pip'], ['python', 's/internal/test-pip-installed.py']))
    test_list.append((['requirements'], ['python', 's/internal/test-pip-requirements.py']))
    test_list.append((['database'], ['python', 's/internal/test-db.py']))

    for pack in packs:
        test_list.append((pack['tags'], ['python', 'manage.py', 'test', '{0}/tests/'.format(pack['path']), '--settings=bluesteel.settings.testing', '--failfast']))

    for pack in packs:
        test_list.append((['pylint'], ['pylint', '--rcfile=s/internal/pylint-config-file.py', '--generated-members=objects', '--msg-template={path}:{line}: [{msg_id}({symbol}), {obj}] {msg}', pack['path']]))

    return test_list

def main(args=sys.argv):

    tag_filter = ""
    if len(args) > 1:
        tag_filter = args[1]

    work_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

    test_list = get_test_list()

    for test in test_list:
        if len(tag_filter) > 0 and (tag_filter not in test[0]):
            continue

        name_test = '{0}'.format(' '.join(test[0])) 

        try:
            result = subprocess.check_call(test[1], cwd=work_dir)
        except subprocess.CalledProcessError, e:
            print 'Tests {0}: {1}'.format(name_test, get_red_string('FAILED'))
            sys.exit(1)
            return
        if result != 0:
            print 'Tests {0}: {1}'.format(name_test, get_red_string('FAILED'))
            sys.exit(1)
            return
        else:
            print 'Tests {0}: {1}'.format(name_test, get_green_string('OK'))
    print 'All tests: ' + get_green_string('OK')
    return

if __name__ == '__main__':
    main()
