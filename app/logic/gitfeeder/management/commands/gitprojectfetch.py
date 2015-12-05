""" Command to send emails """

from django.conf import settings
from django.core.management.base import BaseCommand
from app.logic.gitrepo.models.GitProjectModel import GitProjectEntry
# from django.utils import timezone
# from datetime import timedelta
import os
import shutil
import hashlib
import subprocess

class Command(BaseCommand):
    """ Fetch a git project into the gitrepo """
    args = ''
    help = 'Fetch all the git projects'

    def handle(self, *args, **options):
        """ Fetch the most old git project """
        gitproject_entry = Command.get_oldest_git_project_entry_to_fetch()
        project_name = Command.get_project_unique_name(gitproject_entry)

        if not Command.is_project_folder_present(project_name):
            print 'folder project not present'
            Command.create_tmp_folder_for_git_project(project_name)
            Command.clone_git_project(gitproject_entry, project_name)

        # Command.clear_logs_folder(project_name)

        print 'Heyyyy!!!'


    # f = open(os.devnull, "w")
    # print '    + Reset Hard origin/master'
    # subprocess.call(['git', 'reset', '--hard', 'origin/master'], stdout=f, stderr=f, cwd=northstarFolderPath)
    # subprocess.call(['git', 'clean', '-f', '-d', '-q'], stdout=f, stderr=f, cwd=northstarFolderPath)
    # print '    + Pull origin master'
    # subprocess.call(['git', 'pull', '-r', 'origin', 'master'], stdout=f, stderr=f, cwd=northstarFolderPath)
    # print '    + Checkout master'
    # subprocess.call(['git', 'checkout', 'master'], stdout=f, stderr=f, cwd=northstarFolderPath)
    # print '    + Submodule update'
    # subprocess.call(['git', 'submodule', 'update', '--init', '--recursive'],
        # stdout=f, stderr=f, cwd=northstarFolderPath)


    @staticmethod
    def get_oldest_git_project_entry_to_fetch():
        return GitProjectEntry.objects.order_by('-fetched_at').first()

    @staticmethod
    def get_project_unique_name(project):
        hash_object = hashlib.sha1(project.url)
        hash_str = hash_object.hexdigest()[0:7]
        return 'proj-{0}-{1}'.format(project.id, hash_str)

    @staticmethod
    def is_project_folder_present(folder_name):
        """ Checks if the folder structure exists """
        folder_path = os.path.join(settings.TMP_ROOT, folder_name)
        folder_proj = os.path.join(settings.TMP_ROOT, folder_name, 'project')
        folder_log = os.path.join(settings.TMP_ROOT, folder_name, 'project', 'log')
        if not os.path.exists(folder_path):
            return False

        if not os.path.exists(folder_proj):
            return False

        if not os.path.exists(folder_log):
            return False

        return True

    @staticmethod
    def create_tmp_folder_for_git_project(folder_name):
        """ Creates git rpoject folder structure """
        folder_path = os.path.join(settings.TMP_ROOT, folder_name)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
        os.makedirs(os.path.join(settings.TMP_ROOT, folder_name))
        os.makedirs(os.path.join(settings.TMP_ROOT, folder_name, 'project'))
        os.makedirs(os.path.join(settings.TMP_ROOT, folder_name, 'project', 'log'))

    @staticmethod
    def clear_logs_folder(folder_name):
        logs_path = os.path.join(settings.TMP_ROOT, folder_name, 'project', 'log')
        if os.path.exists(logs_path):
            shutil.rmtree(logs_path)
        os.makedirs(logs_path)

    @staticmethod
    def clone_git_project(project, project_name):
        """ clone a git repo """
        project_cwd = os.path.join(settings.TMP_ROOT, project_name, 'project')
        stdout_path = os.path.join(settings.TMP_ROOT, project_name, 'project', 'log', 'git_clone_stdout.txt')
        stderr_path = os.path.join(settings.TMP_ROOT, project_name, 'project', 'log', 'git_clone_stderr.txt')

        file_stdout = open(stdout_path, 'w')
        file_stderr = open(stderr_path, 'w')

        try:
            subprocess.check_call(
                ['git', 'clone', project.url, 'name'],
                stdout=file_stdout,
                stderr=file_stderr,
                cwd=project_cwd
            )
        except subprocess.CalledProcessError:
            print 'Error!!!'
        else:
            print 'succeed!!!'








