""" Git Parent Model tests """

from django.test import TestCase
from django.test import Client
from django.conf import settings
from django.utils import timezone
from app.service.gitrepo.models.GitProjectModel import GitProjectEntry
from app.service.gitrepo.models.GitHashModel import GitHashEntry
from app.service.gitrepo.models.GitParentModel import GitParentEntry
from datetime import timedelta
import os
import hashlib
import shutil


# Create your tests here.

class GitParentTestCase(TestCase):

    def setUp(self):
        self.git_project1 = GitProjectEntry.objects.create(url='http://test/')

        self.git_hash1 = GitHashEntry.objects.create(
            project=self.git_project1,
            git_hash='0000100001000010000100001000010000100001'
        )

        self.git_hash2 = GitHashEntry.objects.create(
            project=self.git_project1,
            git_hash='0000200002000020000200002000020000200002'
        )

    def tearDown(self):
        pass

    def test_create_git_parent_entry(self):
        entry = GitParentEntry.objects.create(
            project=self.git_project1,
            parent=self.git_hash1,
            son=self.git_hash2,
            order=5
        )

        self.assertEqual('http://test/', entry.project.url)
        self.assertEqual('0000100001000010000100001000010000100001', entry.parent.git_hash)
        self.assertEqual('0000200002000020000200002000020000200002', entry.son.git_hash)
        self.assertEqual(5, entry.order)

    def test_create_git_parent_default(self):
        entry = GitParentEntry.objects.create(
            project=self.git_project1,
            parent=self.git_hash1,
            son=self.git_hash2,
        )

        self.assertEqual(0, entry.order)