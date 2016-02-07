""" ProjectFolderManager tests """

from django.test import TestCase
from django.conf import settings
from django.utils import timezone
from django.utils.six import StringIO
from app.logic.bluesteelworker.download.ProjectFolderManager import ProjectFolderManager
import os
import json
import hashlib
import shutil
import mock

class GitFetcherTestCase(TestCase):

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

    def create_git_hidden_folder(self, root, tmp, archive, name_project):
        path = os.path.join(root, tmp, archive, name_project, 'project', name_project, '.git')
        os.makedirs(path)

    def test_get_project_folder_project_1(self):
        path = '{0}/{1}/{2}'.format(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC')
        self.assertEqual(path, ProjectFolderManager.get_archive_folder_path(self.obj1))

    def test_get_project_folder_project_2(self):
        path = '{0}/{1}/{2}'.format(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC')
        self.assertEqual(path, ProjectFolderManager.get_archive_folder_path(self.obj2))

    def test_is_project_folder_present(self):
        os.makedirs(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1', 'project'))
        self.assertTrue(ProjectFolderManager.is_project_folder_present(self.obj1))

    def test_is_not_project_folder_present(self):
        os.makedirs(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1'))
        self.assertFalse(ProjectFolderManager.is_project_folder_present(self.obj1))

    def test_is_git_project_folder_present(self):
        os.makedirs(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1', 'project', 'test-repo', '.git'))
        self.assertTrue(ProjectFolderManager.is_git_project_folder_present(self.obj1))

    def test_is_not_git_project_folder_present(self):
        os.makedirs(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC'))
        self.assertFalse(ProjectFolderManager.is_git_project_folder_present(self.obj1))

    def test_is_log_project_folder_present(self):
        os.makedirs(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1', 'log'))
        self.assertTrue(ProjectFolderManager.is_log_project_folder_present(self.obj1))

    def test_is_not_log_project_folder_present(self):
        os.makedirs(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC'))
        self.assertFalse(ProjectFolderManager.is_log_project_folder_present(self.obj1))

    def test_create_tmp_folder_for_git_project(self):
        ProjectFolderManager.create_tmp_folder_for_git_project(self.obj1)
        ProjectFolderManager.create_tmp_folder_for_git_project(self.obj2)
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1', 'project')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1', 'log')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-2')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-2', 'project')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-2', 'log')))

    def test_create_tmp_folder_remove_previous_folder(self):
        os.makedirs(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1', 'folder-2'))
        ProjectFolderManager.create_tmp_folder_for_git_project(self.obj1)
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1', 'project')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1', 'log')))
        self.assertFalse(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1', 'folder-2')))
