#!/usr/bin/env python

import subprocess

def main():
    cmd = 'curl --silent --show-error --retry 5 https://bootstrap.pypa.io/get-pip.py | sudo python2.7'
    subprocess.call(cmd, shell=True)

if __name__ == '__main__':
    main()