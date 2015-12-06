#!/usr/bin/env python

import subprocess
import os
import sys

def main():
    subprocess.call(['python', 'manage.py', 'runserver', '0.0.0.0:8080', '--settings=bluesteel.settings.production'])

if __name__ == '__main__':
    main()