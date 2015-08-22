#!/usr/bin/env python

import subprocess
import os
import platform
import sys

def main():
    command = ['./manage.py', 'migrate', '--settings=stronghold.settings.testing']

    out_str = subprocess.check_output(command)

    if ('No migrations to apply' not in out_str) or 'manage.py makemigrations' in out_str:
        print 'Test DB failed becuase:'
        print out_str
        sys.exit(1)

    print '----------------------------------------'
    print 'Tested command: ' + ' '.join(command)
    print 'Out:'
    print out_str
    print '----------------------------------------'

    # We call it again to see color :)
    subprocess.call(command)

if __name__ == '__main__':
    main()
