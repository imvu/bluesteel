#!/usr/bin/env python3

import subprocess
import os
import platform
import sys

def main():
    list_path = os.environ['PATH'].split(os.pathsep)

    if platform.system() == 'Darwin':
        # This is necessary for installing psycopg2 with pip
        # pg_folder = '/Applications/Postgres.app/Contents/Versions/9.3/bin'
        # if os.path.exists(pg_folder):
        #     if not pg_folder in list_path:
        #         os.environ["PATH"] += os.pathsep + pg_folder
        # else:
        #     print '- Folder /Applications/Postgres.app/Contents/Versions/9.3/bin/ does not exist!'
        #     print '    + You need Postgres App installed to let pip use some binaries for compilation time.'
        #     print '    + Did you installed Postgres App ?'
        #     sys.exit(1)
        pass

    elif platform.system() == 'Linux':
        # The command will be something like:
        # sudo apt-get install postgresql postgresql-contrib libpq-dev
        subprocess.call(['apt-get', 'install', 'postgresql', 'postgresql-contrib', 'libpq-dev'])
        subprocess.call(['apt-get', 'install', 'libjpeg-dev'])
        subprocess.call(['apt-get', 'install', 'libjpeg8-dev'])

    elif platform.system() == 'Windows':
        print('- This script needs fix for Windows platform')
        print('- You need to add to the environment the path necessary to install Python module psycho2')
        print('- See Darwin solution')
        sys.exit(1)
    else:
        print('- Your platform is not recognized')
        sys.exit(1)

    subprocess.call(['pip3', 'install', '-r', 'third-party/requirements/pip-requirements.txt'])

if __name__ == '__main__':
    main()
