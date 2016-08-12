""" File Hasher code """

import os
import hashlib

class FileHasher(object):
    """ This code helps us to hash files inside a folder. """

    @staticmethod
    def get_hash_from_files_in_a_folder(folder_path, extensions):
        """ Returns a resulting hash from all the files in the folder """
        if not os.path.exists(folder_path):
            print 'FileHasher can not compute SHA from not found folder: ', folder_path

        sha = hashlib.sha1()

        for root, dirs, files in os.walk(folder_path):
            del dirs
            for names in files:
                if not FileHasher.is_file_name_extensions_allowed(names, extensions):
                    continue

                filepath = os.path.join(root, names)
                file_to_hash = open(filepath, 'rb')

                while True:
                    file_chunk = file_to_hash.read(4096)
                    if not file_chunk:
                        break
                    sha.update(hashlib.sha1(file_chunk).hexdigest())

                file_to_hash.close()

        return sha.hexdigest()

    @staticmethod
    def is_file_name_extensions_allowed(name, extensions):
        """ Checks if a file extensions is allowed """
        for extension in extensions:
            if name.endswith(extension):
                return True
        return False
