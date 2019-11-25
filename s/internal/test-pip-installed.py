 #!/usr/bin/env python3

import subprocess
import os

def main():
    f = open(os.devnull,"w")
    try:
        ret = subprocess.check_call(['pip3', 'help'], stdout = f, stderr = f)
    except subprocess.CalledProcessError as e:
        print('Pip3 not found!')
        print('    - Try: curl --silent --show-error --retry 5 https://bootstrap.pypa.io/get-pip.py | sudo python3')
        print('    - Or: easy_install pip3')
        ret = 1
    return ret

if __name__ == '__main__':
    main()
