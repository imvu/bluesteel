#!/usr/bin/env python

import subprocess
import os
import platform

def main():
    ret = 0
    try:
        ret = subprocess.check_call(['./manage.py', 'migrate', '--settings=stronghold.settings.testing'])
    except subprocess.CalledProcessError, e:
        print 'Database not configured properly!'
        print '    - Try: Install PostgresSQL or SQLlite'
        ret = 1

    if ret:
        sys.exit(1)


if __name__ == '__main__':
    main()
