""" Worker Model tests """

from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.six import StringIO
from app.logic.bluesteelworker.models.WorkerModel import WorkerEntry
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


    def test_get_max_feed_reports_names_and_values(self):
        worker_entry = WorkerEntry.objects.create(
            name='worker-1',
            uuid='1234567890',
            operative_system='osx',
            description='One Worker :)',
            user=self.user1,
            max_feed_reports=30,
        )

        names = worker_entry.get_max_feed_reports_names_and_values()

        self.assertEqual(6, len(names))
        self.assertEqual('10 Reports', names[0]['name'])
        self.assertEqual('20 Reports', names[1]['name'])
        self.assertEqual('30 Reports', names[2]['name'])
        self.assertEqual('40 Reports', names[3]['name'])
        self.assertEqual('50 Reports', names[4]['name'])
        self.assertEqual('100 Reports', names[5]['name'])

        self.assertFalse(names[0]['current'])
        self.assertFalse(names[1]['current'])
        self.assertTrue(names[2]['current'])
        self.assertFalse(names[3]['current'])
        self.assertFalse(names[4]['current'])
        self.assertFalse(names[5]['current'])
