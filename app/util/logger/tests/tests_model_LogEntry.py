""" Log Model tests """

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from app.util.logger.models.LogModel import LogEntry
from datetime import timedelta

class LogEntryTestCase(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user('user1@test.com', 'user1@test.com', 'pass1')
        self.user1.save()

    def tearDown(self):
        pass

    def test_log_debug(self):
        LogEntry.debug(self.user1, 'message-1')

        entry = LogEntry.objects.all().first()

        self.assertEqual(self.user1.id, entry.user.id)
        self.assertEqual(LogEntry.DEBUG, entry.log_type)
        self.assertEqual('message-1', entry.message)

    def test_log_info(self):
        LogEntry.info(self.user1, 'message-2')

        entry = LogEntry.objects.all().first()

        self.assertEqual(self.user1.id, entry.user.id)
        self.assertEqual(LogEntry.INFO, entry.log_type)
        self.assertEqual('message-2', entry.message)

    def test_log_warning(self):
        LogEntry.warning(self.user1, 'message-3')

        entry = LogEntry.objects.all().first()

        self.assertEqual(self.user1.id, entry.user.id)
        self.assertEqual(LogEntry.WARNING, entry.log_type)
        self.assertEqual('message-3', entry.message)

    def test_log_error(self):
        LogEntry.error(self.user1, 'message-4')

        entry = LogEntry.objects.all().first()

        self.assertEqual(self.user1.id, entry.user.id)
        self.assertEqual(LogEntry.ERROR, entry.log_type)
        self.assertEqual('message-4', entry.message)

    def test_log_critical(self):
        LogEntry.critical(self.user1, 'message-5')

        entry = LogEntry.objects.all().first()

        self.assertEqual(self.user1.id, entry.user.id)
        self.assertEqual(LogEntry.CRITICAL, entry.log_type)
        self.assertEqual('message-5', entry.message)
