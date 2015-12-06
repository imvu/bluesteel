#!/usr/bin/env python

import os
import collections

def setup_file_owner():
    this_path = os.getcwd()
    owner_count = []

    for root, dirs, files in os.walk(this_path):
        del dirs
        for file_entry in files:
            owner_uid = os.stat(os.path.join(root, file_entry)).st_uid
            owner_gid = os.stat(os.path.join(root, file_entry)).st_gid
            owner_count.append((owner_uid, owner_gid))

    counter = collections.Counter(owner_count)
    most_common_uid = counter.most_common(1)[0][0][0]
    most_common_gid = counter.most_common(1)[0][0][1]

    for root, dirs, files in os.walk(this_path):
        del dirs
        for file_entry in files:
            file_path = os.path.join(root, file_entry)
            owner_uid = os.stat(file_path).st_uid
            owner_gid = os.stat(file_path).st_gid
            if owner_uid != most_common_uid:
                os.chown(file_path, most_common_uid, most_common_gid)

def main():
    setup_file_owner()

if __name__ == '__main__':
    main()