#!/usr/bin/env python

import subprocess
import os
import sys

def main():

    proc = subprocess.Popen(['pip3', 'freeze'], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    (out, error) = proc.communicate()
    list_pack = out.split(b'\n')
    list_pack = [x.decode("utf-8") for x in list_pack if len(list_pack) > 0]


    req_file = open('third-party/requirements/pip-requirements.txt','r')
    req_file_content = req_file.read()

    list_req = req_file_content.split('\n')
    list_req = [x for x in list_req if len(list_req) > 0]

    for req in list_req:
        if not req in list_pack:
            print('Requirement not found: ' + req)
            print('    - Try: pip3 install ' + req)
            sys.exit(1)


if __name__ == '__main__':
    main()
