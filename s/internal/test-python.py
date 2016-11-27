#!/usr/bin/env python

import subprocess
import os
import platform
import sys

def main():
    command = ['python', '--version']

    try:
        out_str = subprocess.check_output(command, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError, e:
        print 'Command {0} failed!'.format(' '.join(command))
        print 'Error: ', e
        sys.exit(1)

    out_str = out_str.lower().strip()

    if ('python' not in out_str) or ('2.7.' not in out_str):
        print 'Python 2.7.x required, but \'python --version\' returned:'
        print out_str
        sys.exit(1)

    print '----------------------------------------'
    print 'Tested command: ' + ' '.join(command)
    print 'Out: ' + out_str
    print '----------------------------------------'

if __name__ == '__main__':
    main()
