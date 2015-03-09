""" Git Hash Model tests """

from django.test import TestCase
from django.test import Client
from django.conf import settings
from django.utils import timezone
from app.service.gitrepo.models.GitProjectModel import GitProjectEntry
from app.service.gitrepo.models.GitHashModel import GitHashEntry
from datetime import timedelta
import os
import hashlib
import shutil


# Create your tests here.

class GitHashTestCase(TestCase):

    def setUp(self):
        self.git_project1 = GitProjectEntry.objects.create(url='http://test/')

    def tearDown(self):
        pass

    def test_create_git_hash_entry(self):
        entry = GitHashEntry.objects.create(
            project=self.git_project1,
            git_hash='0000100001000010000100001000010000100001',
        )

        self.assertEqual('http://test/', entry.project.url)
        self.assertEqual('0000100001000010000100001000010000100001', entry.git_hash)

    def test_create_git_hash_default(self):
        entry = GitHashEntry.objects.create(
            project=self.git_project1,
        )

        self.assertEqual('http://test/', entry.project.url)
        self.assertEqual('0000000000000000000000000000000000000000', entry.git_hash)