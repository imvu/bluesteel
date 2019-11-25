#!/usr/bin/env python3

import subprocess
import os
import sys
import shutil
import argparse

def parse_arguments():
    """ Argument parsing """
    parser = argparse.ArgumentParser(prog='run-server.py')
    parser.add_argument(
        '--mode',
        help='Indicates if the server will be in development or production mode.',
        dest='server_mode',
        action='store',
        default='development',
        choices=['development', 'production'],
        required=False,
    )

    parser.add_argument(
        '--open',
        help='Indicates if the server will accept incoming connections, by using 0.0.0.0:X',
        dest='server_open',
        action='store',
        default='no',
        choices=['yes', 'no'],
        required=False,
    )

    parser.add_argument(
        '--port',
        help='Indicates which port the server will listen at.',
        dest='server_port',
        action='store',
        type=int,
        default=-1,
        required=False
    )
    return parser.parse_args()

def clean_static_folder():
    """ Cleans the static folder to allow static files to be readed again by collectstatic """
    base_dir = os.path.dirname(os.path.dirname(__file__))
    tmp_dir = os.path.abspath(os.path.join(base_dir, 'tmp'))
    static_dir = os.path.abspath(os.path.join(tmp_dir, 'static'))

    if os.path.exists(static_dir):
        shutil.rmtree(static_dir)
    os.makedirs(static_dir)

def get_settings_string(args):
    if args.server_mode == 'development':
        return '--settings=bluesteel.settings.development'
    else:
        return '--settings=bluesteel.settings.production'

def get_port_string(args):
    if args.server_port > -1:
        return args.server_port
    else:
        if args.server_mode == 'development':
            return '28028'
        else:
            return '8080'

def get_open_string(args):
    if args.server_open == 'yes':
        return '0.0.0.0:'
    else:
        return ''

def main():
    args = parse_arguments()
    clean_static_folder()
    settings_str = get_settings_string(args)
    port_str = get_port_string(args)
    open_str = get_open_string(args)

    subprocess.call(['python3', 's/internal/install-pip-requirements.py'])
    subprocess.call(['python3', 'manage.py', 'makemigrations', settings_str])
    subprocess.call(['python3', 'manage.py', 'migrate', settings_str])
    subprocess.call(['python3', 'manage.py', 'collectstatic', settings_str, '--noinput'])
    subprocess.call(['python3', 'manage.py', 'hash_worker_files', settings_str])
    subprocess.call(['python3', 'manage.py', 'runserver', '{0}{1}'.format(open_str, port_str), settings_str])

if __name__ == '__main__':
    main()
