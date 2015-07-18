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
    packs.append(get_packed_app_info(['app', 'gitrepo'],            'app/service/gitrepo',))
    packs.append(get_packed_app_info(['app', 'gitfeeder'],          'app/service/gitfeeder',))
    packs.append(get_packed_app_info(['app', 'strongholdworker'],   'app/service/strongholdworker',))
    packs.append(get_packed_app_info(['app', 'bluesteel'],          'app/service/bluesteel',))
    packs.append(get_packed_app_info(['app', 'httpcommon'],         'app/util/httpcommon',))
    packs.append(get_packed_app_info(['app', 'commandrepo'],        'app/util/commandrepo',))
    packs.append(get_packed_app_info(['app', 'fontawesome'],        'app/util/fontawesome',))
    packs.append(get_packed_app_info(['app', 'logger'],             'app/util/logger',))
    packs.append(get_packed_app_info(['app', 'presenter'],          'app/presenter',))

    test_list = []
    test_list.append((['pip'], ['python', 's/internal/test-pip-installed.py']))
    test_list.append((['requirements'], ['python', 's/internal/test-pip-requirements.py']))
    test_list.append((['database'], ['python', 's/internal/test-db.py']))

    for pack in packs:
        test_list.append((pack['tags'], ['python', 'manage.py', 'test', '{0}/tests/'.format(pack['path']), '--settings=stronghold.settings.testing']))

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

        try:
            result = subprocess.check_call(test[1], cwd=work_dir)
        except subprocess.CalledProcessError, e:
            print 'Tests: '+ get_red_string('FAILED')
            sys.exit(1)
            return
        if result != 0:
            print 'Tests: ' + get_red_string('FAILED')
            sys.exit(1)
            return
    print 'Tests: ' + get_green_string('OK')
    return

if __name__ == '__main__':
    main()
