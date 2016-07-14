""" Project Folder Manager code """

import os
import shutil

class ProjectFolderManager(object):
    """ This code provides helpers to find project folders """

    @staticmethod
    def get_tmp_directory_from_list_folders(folders_list):
        return os.sep.join(folders_list)

    @staticmethod
    def get_cwd_of_first_git_project_found_in(directory):
        """ Searches for the first .git folder on the project path and returns its location """
        for root, dirs, files in os.walk(directory):
            del files
            for dir_to_check in dirs:
                if dir_to_check == '.git':
                    return root
        return None

    @staticmethod
    def get_folder_paths(cwd, tmp_folders_list, archive_name, project_name, local_search_path):
        """ Returns an object with all the paths needed on a project """

        obj = {}
        obj['temp'] = str(os.path.join(cwd, ProjectFolderManager.get_tmp_directory_from_list_folders(tmp_folders_list)))
        obj['archive'] = str(os.path.join(obj['temp'], archive_name))
        obj['project_name'] = str(os.path.join(obj['archive'], project_name))
        obj['project'] = str(os.path.join(obj['project_name'], 'project'))
        obj['log'] = str(os.path.join(obj['project_name'], 'log'))
        obj['git_project_search_path'] = str(os.path.join(obj['project'], local_search_path))

        if local_search_path == '.' or local_search_path == '':
            obj['git_project_search_path'] = ProjectFolderManager.get_cwd_of_first_git_project_found_in(obj['project'])

        if obj['git_project_search_path'] == None:
            obj['git_project_search_path'] = obj['project'][:]

        obj['temp'] = os.path.normpath(obj['temp'])
        obj['archive'] = os.path.normpath(obj['archive'])
        obj['project_name'] = os.path.normpath(obj['project_name'])
        obj['project'] = os.path.normpath(obj['project'])
        obj['log'] = os.path.normpath(obj['log'])
        obj['git_project_search_path'] = os.path.normpath(obj['git_project_search_path'])
        return obj

    @staticmethod
    def is_project_folder_present(paths):
        """ Checks if the folder structure exists """
        if paths['project'] == None:
            return False

        if not os.path.exists(paths['project']):
            return False
        return True

    @staticmethod
    def is_git_project_folder_present(paths):
        """ Checks if the folder structure exists """
        if not os.path.exists(paths['project']):
            return False

        project_path = ProjectFolderManager.get_cwd_of_first_git_project_found_in(paths['project'])
        if project_path == None:
            return False

        return True

    @staticmethod
    def is_log_project_folder_present(paths):
        """ Checks if the folder structure exists """
        if not os.path.exists(paths['log']):
            return False
        return True

    @staticmethod
    def create_tmp_folder_for_git_project(paths):
        """ Creates git rpoject folder structure """
        if os.path.exists(paths['project_name']):
            shutil.rmtree(paths['project_name'])

        os.makedirs(paths['project'])
        os.makedirs(paths['log'])
