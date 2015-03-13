""" Git Fetch Command tests """

from django.test import TestCase
from django.test import Client
from django.conf import settings
from django.core.management import call_command
from django.utils import timezone
from django.utils.six import StringIO
from app.service.gitrepo.management.commands.gitprojectfetch import Command as fetchCom
from app.service.gitrepo.models.GitProjectModel import GitProjectEntry
from datetime import timedelta
import os
import hashlib
import shutil

# Create your tests here.

class GitProjectFetchCommandTestCase(TestCase):

    def setUp(self):
        self.git_project1 = GitProjectEntry.objects.create(url='http://test/')

    def tearDown(self):
        if os.path.exists(settings.TMP_ROOT):
            shutil.rmtree(settings.TMP_ROOT)

    def test_get_oldest_project_to_fetch(self):
        proj1 = GitProjectEntry.objects.create(url='http://test-1/')
        proj2 = GitProjectEntry.objects.create(url='http://test-2/')
        proj3 = GitProjectEntry.objects.create(url='http://test-3/')

        proj1.fetched_at = timezone.now() - timedelta(seconds=1)
        proj2.fetched_at = timezone.now() - timedelta(seconds=10)
        proj3.fetched_at = timezone.now() - timedelta(seconds=100)

        self.assertEqual(proj3, fetchCom.get_oldest_git_project_entry_to_fetch())

    def test_get_none_if_no_project_to_fetch(self):
        self.git_project1.delete()
        self.assertEqual(None, fetchCom.get_oldest_git_project_entry_to_fetch())

    def test_get_unique_project_name(self):
        project_unique_name = 'proj-{0}-212fabe'.format(self.git_project1.id)
        self.assertEqual(project_unique_name, fetchCom.get_project_unique_name(self.git_project1))

    def test_is_project_folder_present(self):
        os.makedirs(os.path.join(settings.TMP_ROOT, 'folder-1'))
        os.makedirs(os.path.join(settings.TMP_ROOT, 'folder-1', 'project'))
        os.makedirs(os.path.join(settings.TMP_ROOT, 'folder-1', 'project', 'log'))
        self.assertTrue(fetchCom.is_project_folder_present('folder-1'))

    def test_is_project_folder_present_no_project(self):
        os.makedirs(os.path.join(settings.TMP_ROOT, 'folder-1'))
        self.assertFalse(fetchCom.is_project_folder_present('folder-1'))

    def test_is_project_folder_present_no_git(self):
        os.makedirs(os.path.join(settings.TMP_ROOT, 'folder-1'))
        os.makedirs(os.path.join(settings.TMP_ROOT, 'folder-1', 'project'))
        self.assertFalse(fetchCom.is_project_folder_present('folder-1'))

    def test_create_tmp_folder_for_git_project(self):
        fetchCom.create_tmp_folder_for_git_project('folder-name')
        self.assertTrue(os.path.exists(os.path.join(settings.TMP_ROOT, 'folder-name')))
        self.assertTrue(os.path.exists(os.path.join(settings.TMP_ROOT, 'folder-name', 'project')))

    def test_create_tmp_folder_remove_previous_folder(self):
        os.makedirs(os.path.join(settings.TMP_ROOT, 'folder-1'))
        os.makedirs(os.path.join(settings.TMP_ROOT, 'folder-1', 'folder-2'))
        fetchCom.create_tmp_folder_for_git_project('folder-1')
        self.assertTrue(os.path.exists(os.path.join(settings.TMP_ROOT, 'folder-1')))
        self.assertTrue(os.path.exists(os.path.join(settings.TMP_ROOT, 'folder-1', 'project')))
        self.assertFalse(os.path.exists(os.path.join(settings.TMP_ROOT, 'folder-1', 'folder-2')))

    def test_clear_log_folder(self):
        os.makedirs(os.path.join(settings.TMP_ROOT, 'folder-1'))
        os.makedirs(os.path.join(settings.TMP_ROOT, 'folder-1', 'log'))
        file_log = open(os.path.join(settings.TMP_ROOT, 'folder-1', 'log', 'log1.txt'), 'w')
        file_log.close()

        self.assertTrue(os.path.exists(os.path.join(settings.TMP_ROOT, 'folder-1', 'log', 'log1.txt')))
        fetchCom.create_tmp_folder_for_git_project('folder-1')
        self.assertFalse(os.path.exists(os.path.join(settings.TMP_ROOT, 'folder-1', 'log')))
        self.assertFalse(os.path.exists(os.path.join(settings.TMP_ROOT, 'folder-1', 'log', 'log1.txt')))