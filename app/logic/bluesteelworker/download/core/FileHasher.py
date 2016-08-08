""" File Hasher code """

import os
import hashlib

class FileHasher(object):
    """ This code helps us to hash files inside a folder. """

    @staticmethod
    def get_hash_from_files_in_a_folder(folder_path):
        """ Returns a resulting hash from all the files in the folder """
        if not os.path.exists(folder_path):
            print 'FileHasher can not compute SHA from not found folder: ', folder_path

        sha = hashlib.sha1()

        for root, dirs, files in os.walk(folder_path):
            del dirs
            for names in files:
                filepath = os.path.join(root, names)
                file_to_hash = open(filepath, 'rb')

                while True:
                    file_chunk = file_to_hash.read(4096)
                    if not file_chunk:
                        break
                    sha.update(hashlib.sha1(file_chunk).hexdigest())

                file_to_hash.close()

        return sha.hexdigest()
