#!/usr/bin/env python

import subprocess
import os
import sys

def main():

    if not os.getuid() == 0:
        print '- This script needs to be executed with root privileges (sudo).'
        sys.exit(1)

    list_scripts = []
    list_scripts.append('s/internal/install-hooks.py')
    list_scripts.append('s/internal/install-pip.py')
    list_scripts.append('s/internal/install-pip-requirements.py')

    for script in list_scripts:
        subprocess.call(['python', script])

if __name__ == '__main__':
    main()