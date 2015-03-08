#!/usr/bin/env python

import os

def write_pre_commit_tests():
    file_path = '.git/hooks/pre-commit'
    hook_file = open(file_path,'w')
    hook_file.write('python s/test-stronghold.py\n')
    hook_file.close()
    os.chmod(file_path, 0755)

def main():
    write_pre_commit_tests()

if __name__ == '__main__':
    main()