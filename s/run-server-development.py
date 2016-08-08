#!/usr/bin/env python

import subprocess
import os
import sys

def main():
    subprocess.call(['python', 's/internal/install-pip-requirements.py'])
    subprocess.call(['python', 'manage.py', 'migrate', '--settings=bluesteel.settings.development'])
    subprocess.call(['python', 'manage.py', 'hash_worker_files', '--settings=bluesteel.settings.production'])
    subprocess.call(['python', 'manage.py', 'runserver', '28028', '--settings=bluesteel.settings.development'])

if __name__ == '__main__':
    main()
