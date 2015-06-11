""" Command Result Model tests """

from django.test import TestCase
from django.test import Client
from django.conf import settings
from django.utils import timezone
from app.util.commandrepo.models.CommandGroupModel import CommandGroupEntry
from app.util.commandrepo.models.CommandSetModel import CommandSetEntry
from app.util.commandrepo.models.CommandModel import CommandEntry
from app.util.commandrepo.models.CommandResultModel import CommandResultEntry
from app.util.commandrepo.helper import TestCommandHelper
from datetime import timedelta
import os
import hashlib
import shutil


class CommandResultEntryTestCase(TestCase):

    def setUp(self):
        self.group = CommandGroupEntry.objects.create()
        self.command_set = CommandSetEntry.objects.create(
            group=self.group
        )

    def tearDown(self):
        pass

    def test_create_command_entry_and_as_obj(self):
        date_now = timezone.now()

        command_entry = TestCommandHelper.create_default_command()

        command_result = CommandResultEntry.objects.create(
            command=command_entry,
            out='out_string',
            error='error_string',
            status=0,
            created_at=date_now,
        )

        obj = command_result.as_object()
        self.assertEqual('out_string', obj['out'])
        self.assertEqual('error_string', obj['error'])
        self.assertEqual(0, obj['status'])
