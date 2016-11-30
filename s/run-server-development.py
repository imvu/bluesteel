#!/usr/bin/env python

import subprocess
import os
import sys

def main():
    settings_str = '--settings=bluesteel.settings.development'

    subprocess.call(['python', 's/internal/install-pip-requirements.py'])
    subprocess.call(['python', 'manage.py', 'makemigrations', settings_str])
    subprocess.call(['python', 'manage.py', 'migrate', settings_str])
    subprocess.call(['python', 'manage.py', 'hash_worker_files', settings_str])
    subprocess.call(['python', 'manage.py', 'runserver', '28028', settings_str])

if __name__ == '__main__':
    main()
