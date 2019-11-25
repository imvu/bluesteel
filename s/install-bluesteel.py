#!/usr/bin/env python3

import subprocess
import os
import sys

def main():
    list_commands = []
    list_commands.append(['python3', 's/internal/install-hooks.py'])
    list_commands.append(['python3', 's/internal/install-pip-requirements.py'])
    list_commands.append(['./manage.py', 'makemigrations'])
    list_commands.append(['./manage.py', 'migrate'])
    list_commands.append(['python3', 's/internal/setup-file-owner.py'])

    for command in list_commands:
        subprocess.call(command)

if __name__ == '__main__':
    main()
