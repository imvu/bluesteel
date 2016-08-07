#!/usr/bin/env python

import subprocess
import os
import sys
import shutil

def main():

    base_dir = os.path.dirname(os.path.dirname(__file__))
    tmp_dir = os.path.abspath(os.path.join(base_dir, 'tmp'))
    static_dir = os.path.abspath(os.path.join(tmp_dir, 'static'))

    print static_dir

    if os.path.exists(static_dir):
        shutil.rmtree(static_dir)
    os.makedirs(static_dir)

    subprocess.call(['python', 'manage.py', 'migrate', '--settings=bluesteel.settings.production'])
    subprocess.call(['python', 'manage.py', 'collectstatic', '--settings=bluesteel.settings.production', '--noinput'])
    subprocess.call(['python', 'manage.py', 'runserver', '0.0.0.0:8080', '--settings=bluesteel.settings.production'])

if __name__ == '__main__':
    main()
