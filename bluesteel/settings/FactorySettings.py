import random
import string
import os
import json

SECRET_FILE_NAME = 'Secret-Key-File.josn'
DATABASE_SETTINGS_FILE_NAME = 'Database-Settings-File.json'

def make_random_secret_key():
    """ Returns a secret key with length of 50 """

    char_choice = "{0}{1}{2}".format(string.ascii_letters, string.digits, string.punctuation)
    return ''.join([random.SystemRandom().choice(char_choice) for i in range(50)])

def make_secret_file(file_path):
    """ Creates a file with a json object containing the secret key. """

    secret_key = make_random_secret_key()
    with open(file_path, 'w') as secret_file:
        secret_file.write(json.dumps({'secret_key' : secret_key}))

    return secret_key

def read_secret_file(file_path):
    """ Reads the content of the secret file and returns the secret key. """

    with open(file_path, 'r') as secret_file:
        content = secret_file.read()
        obj = json.loads(content)
        return obj['secret_key']

    print('Secret key faile failed to open!!')
    return ''


def read_database_settings_file(file_path):
    """ Reads the content of the database settings file and returns an object. """

    with open(file_path, 'r') as secret_file:
        content = secret_file.read()
        obj = json.loads(content)
        return (True, obj)

    return (False, {})

def get_secret_key(secret_key_file_path):
    """ Returns the secret key, generated if first time or read from the secret file. """
    file_path = os.path.join(secret_key_file_path, SECRET_FILE_NAME)

    if not os.path.exists(file_path):
        return make_secret_file(file_path)
    else:
        return read_secret_file(file_path)


def get_database_settings(db_settings_path):
    """ Returns an object with the database settings """
    file_path = os.path.join(db_settings_path, DATABASE_SETTINGS_FILE_NAME)

    if not os.path.exists(file_path):
        return (False, {})
    else:
        return read_database_settings_file(file_path)
