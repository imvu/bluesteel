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
    def remove_non_ascii(text):
        """ Removes all the non ascii (7bit) characters """
        return ''.join([i if ord(i) < 128 else ' ' for i in text])

    @staticmethod
    def execute_command_list(command_list, output_folder_path, project_cwd, exit_on_fail):
        """ Executes a list of commands, if the command fails it returns inmediately """
        reports = {}
        reports['commands'] = []

        out_file_path = os.path.join(output_folder_path, 'out.txt')
        err_file_path = os.path.join(output_folder_path, 'err.txt')

        for command in command_list:
            CommandExecutioner.clear_folder(output_folder_path)
            file_stdout = open(out_file_path, 'w')
            file_stderr = open(err_file_path, 'w')

            start_time = datetime.datetime.utcnow().isoformat()

            report = {}
            report['result'] = {}
            report['result']['out'] = ''
            report['result']['error'] = ''
            report['result']['status'] = 0

            normalized_cwd = os.path.normpath(project_cwd)
            exception_msg = ''

            if isinstance(command, str):
                command = command.split(' ')

            try:
                subprocess.check_call(
                    command,
                    stdout=file_stdout,
                    stderr=file_stderr,
                    cwd=normalized_cwd
                )
                report['result']['status'] = 0
            except subprocess.CalledProcessError as error:
                report['result']['status'] = error.returncode
            except OSError as error:
                report['result']['status'] = -1
                exception_msg = '{0}\n'.format(str(error))

            finish_time = datetime.datetime.utcnow().isoformat()

            file_stdout.close()
            file_stderr.close()

            file_stdout = open(out_file_path, 'r')
            file_stderr = open(err_file_path, 'r')

            out = CommandExecutioner.remove_non_ascii(file_stdout.read())
            err = CommandExecutioner.remove_non_ascii(file_stderr.read())

            report['command'] = ' '.join(command)
            report['result']['out'] = out
            report['result']['error'] = '{0}{1}'.format(exception_msg, err)
            report['result']['start_time'] = str(start_time)
            report['result']['finish_time'] = str(finish_time)

            reports['commands'].append(report)

            file_stdout.close()
            file_stderr.close()

            if report['result']['status'] != 0 and exit_on_fail:
                break

        return reports
