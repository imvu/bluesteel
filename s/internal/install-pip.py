#!/usr/bin/env python3

import subprocess

def main():
    cmd = 'curl --silent --show-error --retry 5 https://bootstrap.pypa.io/get-pip.py | sudo python3'
    subprocess.call(cmd, shell=True)

if __name__ == '__main__':
    main()
