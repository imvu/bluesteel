#!/usr/bin/env python3

import subprocess
import os
import platform
import sys

def main():
    command = ['python3', '--version']

    try:
        out_str = subprocess.check_output(command, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print('Command {0} failed!'.format(' '.join(command)))
        print('Error: ', e)
        sys.exit(1)

    out_str = out_str.lower().strip()

    if (b'python' not in out_str) or (b'3.6.' not in out_str):
        print('Python 3.6.x required, but \'python3 --version\' returned:')
        print(out_str)
        sys.exit(1)

    print('----------------------------------------')
    print('Tested command: ' + ' '.join(command))
    print('Out: ' + str(out_str))
    print('----------------------------------------')

if __name__ == '__main__':
    main()
