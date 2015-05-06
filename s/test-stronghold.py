#!/usr/bin/env python

import subprocess
import errno
import sys
import os

def get_red_string(string):
    return '\033[91m' + string + '\033[0m'

def get_green_string(string):
    return '\033[92m' + string + '\033[0m'

def get_test_list():
    """ Returns a list of tests, every test its a list of commands """
    test_list = []
    test_list.append((['pip'], ['python', 's/internal/test-pip-installed.py']))
    test_list.append((['requirements'], ['python', 's/internal/test-pip-requirements.py']))
    test_list.append((['database'], ['python', 's/internal/test-db.py']))
    test_list.append((['app', 'gitrepo'], ['python', 'manage.py', 'test', 'app/service/gitrepo/tests/', '--settings=stronghold.settings.testing']))
    test_list.append((['app', 'gitfeeder'], ['python', 'manage.py', 'test', 'app/service/gitfeeder/tests/', '--settings=stronghold.settings.testing']))
    test_list.append((['app', 'strongholdworker'], ['python', 'manage.py', 'test', 'app/service/strongholdworker/tests/', '--settings=stronghold.settings.testing']))
    test_list.append((['app', 'httpcommon'], ['python', 'manage.py', 'test', 'app/util/httpcommon/tests/', '--settings=stronghold.settings.testing']))
    test_list.append((['app', 'commandrepo'], ['python', 'manage.py', 'test', 'app/util/commandrepo/tests/', '--settings=stronghold.settings.testing']))
    test_list.append((['pylint'], ['pylint', '--rcfile=s/internal/pylint-config-file.py', '--generated-members=objects', '--msg-template={path}:{line}: [{msg_id}({symbol}), {obj}] {msg}', 'app/service/gitrepo']))
    test_list.append((['pylint'], ['pylint', '--rcfile=s/internal/pylint-config-file.py', '--generated-members=objects', '--msg-template={path}:{line}: [{msg_id}({symbol}), {obj}] {msg}', 'app/service/gitfeeder']))
    test_list.append((['pylint'], ['pylint', '--rcfile=s/internal/pylint-config-file.py', '--generated-members=objects', '--msg-template={path}:{line}: [{msg_id}({symbol}), {obj}] {msg}', 'app/service/strongholdworker']))
    test_list.append((['pylint'], ['pylint', '--rcfile=s/internal/pylint-config-file.py', '--generated-members=objects', '--msg-template={path}:{line}: [{msg_id}({symbol}), {obj}] {msg}', 'app/util/httpcommon']))
    test_list.append((['pylint'], ['pylint', '--rcfile=s/internal/pylint-config-file.py', '--generated-members=objects', '--msg-template={path}:{line}: [{msg_id}({symbol}), {obj}] {msg}', 'app/util/commandrepo']))
    return test_list

def main(args=sys.argv):

    tag_filter = ""
    if len(args) > 1:
        tag_filter = args[1]

    work_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

    for test in get_test_list():
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