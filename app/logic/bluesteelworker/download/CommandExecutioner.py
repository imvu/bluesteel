""" Command Executioner code """

import os
import subprocess
import shutil
import datetime

class CommandExecutioner(object):
    """ This code helps us with executing a list of commands and return its outputs. """

    @staticmethod
    def clear_folder(output_folder_path):
        """ Remove and re-creates the output folder """
        if os.path.exists(output_folder_path):
            shutil.rmtree(output_folder_path)
        os.makedirs(output_folder_path)

    @staticmethod
    def execute_command_list(command_list, output_folder_path, project_cwd):
        """ Executes a list of commands, if the command fails it returns inmediately """
        reports = {}
        reports['commands'] = []

        out_file_path = os.path.join(output_folder_path, 'out.txt')
        err_file_path = os.path.join(output_folder_path, 'err.txt')

        for command in command_list:
            CommandExecutioner.clear_folder(output_folder_path)
            file_stdout = open(out_file_path, 'w')
            file_stderr = open(err_file_path, 'w')

            report = {}
            report['result'] = {}
            report['result']['out'] = ''
            report['result']['error'] = ''
            report['result']['status'] = 0

            start_time = datetime.datetime.utcnow().isoformat()

            status = subprocess.call(
                command,
                stdout=file_stdout,
                stderr=file_stderr,
                cwd=os.path.normpath(project_cwd)
            )

            finish_time = datetime.datetime.utcnow().isoformat()

            report['result']['status'] = status

            file_stdout.close()
            file_stderr.close()

            file_stdout = open(out_file_path, 'r')
            file_stderr = open(err_file_path, 'r')

            report['command'] = ' '.join(command)
            report['result']['out'] = file_stdout.read()
            report['result']['error'] = file_stderr.read()
            report['result']['start_time'] = start_time
            report['result']['finish_time'] = finish_time

            reports['commands'].append(report)

            file_stdout.close()
            file_stderr.close()

            if report['result']['status'] != 0:
                break

        return reports
