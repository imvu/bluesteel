#!/usr/bin/env python

import subprocess
import os
import sys

def main():
    subprocess.call(['python', 'manage.py', 'runserver', '28028', '--settings=bluesteel.settings.development'])

if __name__ == '__main__':
    main()