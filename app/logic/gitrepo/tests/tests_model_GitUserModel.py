""" Git User Model tests """

from django.test import TestCase
from django.test import Client
from django.conf import settings
from django.utils import timezone
from app.logic.gitrepo.models.GitProjectModel import GitProjectEntry
from app.logic.gitrepo.models.GitUserModel import GitUserEntry
from datetime import timedelta
import os
import hashlib
import shutil


# Create your tests here.

class GitUserTestCase(TestCase):

    def setUp(self):
        self.git_project1 = GitProjectEntry.objects.create(url='http://test/')

    def tearDown(self):
        pass

    def test_create_git_user_entry(self):
        entry = GitUserEntry.objects.create(
            project=self.git_project1,
            name='user1',
            email='user1@test.com'
        )

        self.assertEqual('http://test/', entry.project.url)
        self.assertEqual('user1', entry.name)
        self.assertEqual('user1@test.com', entry.email)
