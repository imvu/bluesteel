""" Log Model tests """

from django.test import TestCase
from django.utils import timezone
from app.util.logger.models.LogModel import LogEntry
from datetime import timedelta

class LogEntryTestCase(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_log_debug(self):
        LogEntry.debug('message-1')

        entry = LogEntry.objects.all().first()

        self.assertEqual(LogEntry.DEBUG, entry.log_type)
        self.assertEqual('message-1', entry.message)

    def test_log_info(self):
        LogEntry.info('message-2')

        entry = LogEntry.objects.all().first()

        self.assertEqual(LogEntry.INFO, entry.log_type)
        self.assertEqual('message-2', entry.message)

    def test_log_warning(self):
        LogEntry.warning('message-3')

        entry = LogEntry.objects.all().first()

        self.assertEqual(LogEntry.WARNING, entry.log_type)
        self.assertEqual('message-3', entry.message)

    def test_log_error(self):
        LogEntry.error('message-4')

        entry = LogEntry.objects.all().first()

        self.assertEqual(LogEntry.ERROR, entry.log_type)
        self.assertEqual('message-4', entry.message)

    def test_log_critical(self):
        LogEntry.critical('message-5')

        entry = LogEntry.objects.all().first()

        self.assertEqual(LogEntry.CRITICAL, entry.log_type)
        self.assertEqual('message-5', entry.message)
