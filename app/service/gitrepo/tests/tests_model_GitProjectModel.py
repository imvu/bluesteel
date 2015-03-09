""" Git Project Model tests """

from django.test import TestCase
from django.test import Client
from django.conf import settings
from django.utils import timezone
from app.service.gitrepo.models.GitProjectModel import GitProjectEntry
from datetime import timedelta
import os
import hashlib
import shutil


# Create your tests here.

class GitProjectTestCase(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_git_project_entry(self):
        entry = GitProjectEntry.objects.create(url='http://test/')

        self.assertEqual('http://test/', entry.url)
