""" Worker Model tests """

from django.test import TestCase
from django.conf import settings
from django.utils import timezone
from django.utils.six import StringIO
from app.service.strongholdworker.models.WorkerModel import WorkerEntry
from datetime import timedelta
import os
import json
import hashlib
import shutil
import mock

class GitFetcherTestCase(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_worker_and_as_object(self):
        worker_entry = WorkerEntry.objects.create(
            name='worker-1',
            uuid='1234567890',
            description='One Worker :)'
        )

        obj = worker_entry.as_object()

        self.assertEqual('worker-1', obj['name'])
        self.assertEqual('1234567890', obj['uuid'])
        self.assertEqual('One Worker :)', obj['description'])
