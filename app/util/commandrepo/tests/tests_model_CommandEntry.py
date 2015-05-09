""" Command Model tests """

from django.test import TestCase
from django.test import Client
from django.conf import settings
from django.utils import timezone
from app.util.commandrepo.models.CommandReportModel import CommandReportEntry
from app.util.commandrepo.models.CommandSetModel import CommandSetEntry
from app.util.commandrepo.models.CommandModel import CommandEntry
from datetime import timedelta
import os
import hashlib
import shutil


class CommandEntryTestCase(TestCase):

    def setUp(self):
        self.report = CommandReportEntry.objects.create()
        self.command_set = CommandSetEntry.objects.create(
            report=self.report
        )

    def tearDown(self):
        pass

    def test_create_command_entry_and_as_obj(self):
        date_now = timezone.now()

        command = CommandEntry.objects.create(
            command_set=self.command_set,
            command='["command1", "arg1", "arg2"]',
            out='out_string',
            error='error_string',
            exception='exception_string',
            status=CommandEntry.OK,
            created_at=date_now,
        )

        obj = command.as_object()
        self.assertEqual(['command1', 'arg1', 'arg2'], obj['command'])
        self.assertEqual('out_string', obj['out'])
        self.assertEqual('error_string', obj['error'])
        self.assertEqual('exception_string', obj['exception'])
        self.assertEqual('OK', obj['status'])
        self.assertLess(date_now, obj['date_created_at'])

    def test_set_status_from_str(self):
        date_now = timezone.now()

        command = CommandEntry.objects.create(
            command_set=self.command_set,
            command='["command1", "arg1", "arg2"]',
            out='out_string',
            error='error_string',
            exception='exception_string',
            status=CommandEntry.OK,
            created_at=date_now,
        )

        command.set_status_from_str('ERROR')
        self.assertEqual(CommandEntry.ERROR, command.status)
        command.set_status_from_str('VALUE')
        self.assertEqual(CommandEntry.ERROR, command.status)
        command.set_status_from_str('OK')
        self.assertEqual(CommandEntry.OK, command.status)
