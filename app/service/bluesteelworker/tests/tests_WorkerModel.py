""" Worker Model tests """

from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.six import StringIO
from app.service.bluesteelworker.models.WorkerModel import WorkerEntry
from datetime import timedelta
import os
import json
import hashlib
import shutil
import mock

class WorkerModelTestCase(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user('user1@test.com', 'user1@test.com', 'pass1')
        self.user1.save()
        pass

    def tearDown(self):
        pass

    def test_create_worker_and_as_object(self):
        worker_entry = WorkerEntry.objects.create(
            name='worker-1',
            uuid='1234567890',
            operative_system='osx',
            description='One Worker :)',
            user=self.user1
        )

        obj = worker_entry.as_object()

        self.assertEqual(worker_entry.user.id, obj['id'])
        self.assertEqual('worker-1', obj['name'])
        self.assertEqual('1234567890', obj['uuid'])
        self.assertEqual('osx', obj['operative_system'])
        self.assertEqual('One Worker :)', obj['description'])
        self.assertEqual(False, obj['git_feeder'])
