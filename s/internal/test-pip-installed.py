 #!/usr/bin/env python

import subprocess
import os

def main():
    f = open(os.devnull,"w")
    try:
        ret = subprocess.check_call(['pip', 'help'], stdout = f, stderr = f)
    except subprocess.CalledProcessError, e:
        print 'Pip not found!'
        print '    - Try: curl --silent --show-error --retry 5 https://bootstrap.pypa.io/get-pip.py | sudo python2.7'
        print '    - Or: easy_install pip'
        ret = 1
    return ret

if __name__ == '__main__':
    main()