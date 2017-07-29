""" ProjectFolderManager tests """

from django.test import TestCase
from django.conf import settings
from django.utils import timezone
from django.utils.six import StringIO
from app.logic.bluesteelworker.download.core.ProjectFolderManager import ProjectFolderManager
import os
import json
import hashlib
import shutil
import mock

class ProjectFolderManagerTestCase(TestCase):

    def setUp(self):
        self.tmp_folder = os.path.join(settings.TMP_ROOT)

        if not os.path.exists(self.tmp_folder):
            os.makedirs(self.tmp_folder)

        self.obj1 = {}
        self.obj1['git'] = {}
        self.obj1['git']['project'] = {}
        self.obj1['git']['project']['current_working_directory'] = self.tmp_folder
        self.obj1['git']['project']['tmp_directory'] = ['tmp-gitfetcher-folder']
        self.obj1['git']['project']['archive'] = 'archive-28-0123ABC'
        self.obj1['git']['project']['name'] = 'test-repo-1'
        self.obj1['git']['project']['url'] = 'git-url'
        self.obj1['git']['branches'] = []
        self.obj1['git']['clone'] = {}
        self.obj1['git']['clone']['commands'] = []
        self.obj1['git']['clone']['commands'].append(['git','clone','https://llorensmarti@bitbucket.org/llorensmarti/test-repo.git'])
        self.obj1['git']['clone']['commands'].append(['git','submodule','update', '--init', '--recursive'])
        self.obj1['git']['fetch'] = {}
        self.obj1['git']['fetch']['commands'] = []
        self.obj1['git']['fetch']['commands'].append(['git', 'reset', '--hard', 'origin/master'])
        self.obj1['git']['fetch']['commands'].append(['git', 'clean', '-f', '-d', '-q'])
        self.obj1['git']['fetch']['commands'].append(['git', 'pull', '-r', 'origin', 'master'])
        self.obj1['git']['fetch']['commands'].append(['git', 'checkout', 'master'])
        self.obj1['git']['fetch']['commands'].append(['git', 'submodule', 'update', '--init', '--recursive'])

        self.obj2 = {}
        self.obj2['git'] = {}
        self.obj2['git']['project'] = {}
        self.obj2['git']['project']['current_working_directory'] = self.tmp_folder
        self.obj2['git']['project']['tmp_directory'] = ['tmp-gitfetcher-folder']
        self.obj2['git']['project']['archive'] = 'archive-28-0123ABC'
        self.obj2['git']['project']['name'] = 'test-repo-2'
        self.obj2['git']['project']['url'] = 'git-url'
        self.obj2['git']['branches'] = []
        self.obj2['git']['clone'] = {}
        self.obj2['git']['clone']['commands'] = []
        self.obj2['git']['clone']['commands'].append(['git','clone','https://llorensmarti@bitbucket.org/llorensmarti/test-repo.git'])
        self.obj2['git']['clone']['commands'].append(['git','submodule','update', '--init', '--recursive'])
        self.obj2['git']['fetch'] = {}
        self.obj2['git']['fetch']['commands'] = []
        self.obj2['git']['fetch']['commands'].append(['git', 'reset', '--hard', 'origin/master'])
        self.obj2['git']['fetch']['commands'].append(['git', 'clean', '-f', '-d', '-q'])
        self.obj2['git']['fetch']['commands'].append(['git', 'pull', '-r', 'origin', 'master'])
        self.obj2['git']['fetch']['commands'].append(['git', 'checkout', 'master'])
        self.obj2['git']['fetch']['commands'].append(['git', 'submodule', 'update', '--init', '--recursive'])

    def tearDown(self):
        if os.path.exists(self.tmp_folder):
            shutil.rmtree(self.tmp_folder)

    def create_project_folders(self):
        paths = ProjectFolderManager.get_folder_paths(
            self.tmp_folder,
            ['tmp', 'folder', 'list'],
            'archive-name',
            'project-name',
            'test-repo'
        )

        ProjectFolderManager.create_tmp_folder_for_git_project(paths)
        return paths

    def create_project_folders_with_git_hidden_folder(self):
        paths = ProjectFolderManager.get_folder_paths(
            self.tmp_folder,
            ['tmp', 'folder', 'list'],
            'archive-name',
            'project-name',
            'test-repo-2'
        )

        ProjectFolderManager.create_tmp_folder_for_git_project(paths)
        os.makedirs(os.path.join(paths['project'], 'test-repo-1/.git'))
        os.makedirs(os.path.join(paths['project'], 'test-repo-2/.git'))
        os.makedirs(os.path.join(paths['project'], 'test-repo-3/.git'))
        return paths

    def test_generated_folder_paths_are_correct(self):
        paths = ProjectFolderManager.get_folder_paths(
            self.tmp_folder,
            ['tmp', 'folder', 'list'],
            'archive-name',
            'project-name',
            'test-repo'
        )

        self.assertEqual(os.path.join(self.tmp_folder, 'tmp/folder/list'), paths['temp'])
        self.assertEqual(os.path.join(self.tmp_folder, 'tmp/folder/list/archive-name'), paths['archive'])
        self.assertEqual(os.path.join(self.tmp_folder, 'tmp/folder/list/archive-name/project-name'), paths['project_name'])
        self.assertEqual(os.path.join(self.tmp_folder, 'tmp/folder/list/archive-name/project-name/project'), paths['project'])
        self.assertEqual(os.path.join(self.tmp_folder, 'tmp/folder/list/archive-name/project-name/log'), paths['log'])
        self.assertEqual(os.path.join(self.tmp_folder, 'tmp/folder/list/archive-name/project-name/project/test-repo'), paths['git_project_search_path'])

    def test_if_local_search_path_is_dot_and_no_project_folder_then_path_equal_project(self):
        paths = ProjectFolderManager.get_folder_paths(
            self.tmp_folder,
            ['tmp', 'folder', 'list'],
            'archive-name',
            'project-name',
            '.'
        )

        self.assertEqual(os.path.join(self.tmp_folder, 'tmp/folder/list'), paths['temp'])
        self.assertEqual(os.path.join(self.tmp_folder, 'tmp/folder/list/archive-name'), paths['archive'])
        self.assertEqual(os.path.join(self.tmp_folder, 'tmp/folder/list/archive-name/project-name'), paths['project_name'])
        self.assertEqual(os.path.join(self.tmp_folder, 'tmp/folder/list/archive-name/project-name/project'), paths['project'])
        self.assertEqual(os.path.join(self.tmp_folder, 'tmp/folder/list/archive-name/project-name/log'), paths['log'])
        self.assertEqual(os.path.join(self.tmp_folder, 'tmp/folder/list/archive-name/project-name/project'), paths['git_project_search_path'])

    def test_if_local_search_path_is_dot_folder_then_path_equal_first_git_project(self):
        os.makedirs(os.path.join(self.tmp_folder, 'tmp/folder/list/archive-name/project-name/project/test-repo-1/.git'))
        os.makedirs(os.path.join(self.tmp_folder, 'tmp/folder/list/archive-name/project-name/project/test-repo-2/.git'))
        os.makedirs(os.path.join(self.tmp_folder, 'tmp/folder/list/archive-name/project-name/project/test-repo-3/.git'))
        paths = ProjectFolderManager.get_folder_paths(
            self.tmp_folder,
            ['tmp', 'folder', 'list'],
            'archive-name',
            'project-name',
            '.'
        )

        self.assertEqual(os.path.join(self.tmp_folder, 'tmp/folder/list'), paths['temp'])
        self.assertEqual(os.path.join(self.tmp_folder, 'tmp/folder/list/archive-name'), paths['archive'])
        self.assertEqual(os.path.join(self.tmp_folder, 'tmp/folder/list/archive-name/project-name'), paths['project_name'])
        self.assertEqual(os.path.join(self.tmp_folder, 'tmp/folder/list/archive-name/project-name/project'), paths['project'])
        self.assertEqual(os.path.join(self.tmp_folder, 'tmp/folder/list/archive-name/project-name/log'), paths['log'])
        self.assertEqual(os.path.join(self.tmp_folder, 'tmp/folder/list/archive-name/project-name/project/test-repo-1'), paths['git_project_search_path'])

    def test_is_project_folder_present(self):
        paths = self.create_project_folders()
        self.assertTrue(ProjectFolderManager.is_project_folder_present(paths))

    def test_is_not_project_folder_present(self):
        paths = {}
        paths['project'] = os.path.join(self.tmp_folder, 'folder/that/does/not/exist')

        self.assertFalse(ProjectFolderManager.is_project_folder_present(paths))

    def test_is_git_project_folder_present(self):
        paths = self.create_project_folders_with_git_hidden_folder()
        self.assertTrue(ProjectFolderManager.is_git_project_folder_present(paths))

    def test_is_not_git_project_folder_present(self):
        paths = ProjectFolderManager.get_folder_paths(
            self.tmp_folder,
            ['tmp', 'folder', 'list'],
            'archive-name',
            'project-name',
            'test-repo-with-no-git'
        )

        self.assertFalse(ProjectFolderManager.is_git_project_folder_present(paths))

    def test_is_log_project_folder_present(self):
        paths = self.create_project_folders()
        self.assertTrue(ProjectFolderManager.is_log_project_folder_present(paths))

    def test_is_not_log_project_folder_present(self):
        paths = ProjectFolderManager.get_folder_paths(
            self.tmp_folder,
            ['tmp', 'folder', 'list'],
            'archive-name',
            'project-name',
            'test-repo'
        )

        self.assertFalse(ProjectFolderManager.is_log_project_folder_present(paths))

    def test_create_tmp_folder_for_git_project(self):
        paths = ProjectFolderManager.get_folder_paths(
            self.tmp_folder,
            ['tmp', 'folder', 'list'],
            'archive-name',
            'project-name',
            'test-repo'
        )

        ProjectFolderManager.create_tmp_folder_for_git_project(paths)
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp/folder/list', 'archive-name')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp/folder/list', 'archive-name', 'project-name')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp/folder/list', 'archive-name', 'project-name', 'project')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp/folder/list', 'archive-name', 'project-name', 'log')))

    def test_create_tmp_folder_remove_previous_folder(self):
        os.makedirs(os.path.join(self.tmp_folder, 'tmp/folder/list', 'archive-name', 'project-name', 'folder-to-be-removed'))

        paths = ProjectFolderManager.get_folder_paths(
            self.tmp_folder,
            ['tmp', 'folder', 'list'],
            'archive-name',
            'project-name',
            'test-repo'
        )

        ProjectFolderManager.create_tmp_folder_for_git_project(paths)
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp/folder/list', 'archive-name')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp/folder/list', 'archive-name', 'project-name')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp/folder/list', 'archive-name', 'project-name', 'project')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp/folder/list', 'archive-name', 'project-name', 'log')))
        self.assertFalse(os.path.exists(os.path.join(self.tmp_folder, 'tmp/folder/list', 'archive-name', 'project-name', 'folder-to-be-removed')))

