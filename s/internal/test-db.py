#!/usr/bin/env python

import subprocess
import os
import platform
import sys

def main():
    command = ['./manage.py', 'migrate', '--settings=stronghold.settings.testing']

    out_str = subprocess.check_output(command)
    subprocess.call(command)

    if 'No migrations to apply' not in out_str:
        sys.exit(1)

if __name__ == '__main__':
    main()
