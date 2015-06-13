""" Command Model tests """

from django.test import TestCase
from django.test import Client
from django.conf import settings
from django.utils import timezone
from app.util.commandrepo.models.CommandGroupModel import CommandGroupEntry
from app.util.commandrepo.models.CommandSetModel import CommandSetEntry
from app.util.commandrepo.models.CommandModel import CommandEntry
from datetime import timedelta
import os
import hashlib
import shutil


class CommandEntryTestCase(TestCase):

    def setUp(self):
        self.group = CommandGroupEntry.objects.create()
        self.command_set = CommandSetEntry.objects.create(
            group=self.group
        )

    def tearDown(self):
        pass

    def test_create_command_entry_and_as_obj(self):
        date_now = timezone.now()

        command = CommandEntry.objects.create(
            command_set=self.command_set,
            command='command1 arg1 arg2',
            created_at=date_now,
        )

        obj = command.as_object()
        self.assertEqual('command1 arg1 arg2', obj['command'])
        # self.assertLess(date_now, obj['date_created_at'])
