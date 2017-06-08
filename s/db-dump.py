#!/usr/bin/env python

import subprocess
import os
import sys
import zipfile
import datetime

def main():
    command = ['./manage.py', 'dumpdata']

    proc = subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    (out, error) = proc.communicate()

    date = datetime.datetime.now()
    file_name = 'bluesteel-backup-{0}.zip'.format(date.strftime("%Y-%m-%d_%H:%M:%S"))

    with zipfile.ZipFile(os.path.join('.', 'tmp', file_name), "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('data.json', out)

if __name__ == '__main__':
    main()
