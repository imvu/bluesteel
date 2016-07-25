""" Mailing controller tests """

from django.test import TestCase
from django.conf import settings
from django.core import mail
from app.logic.mailing.models.StackedMailModel import StackedMailEntry
from app.logic.mailing.controllers import MailingController
import os
import shutil


class MailingControllerTestCase(TestCase):

    def setUp(self):
        self.tmp_folder = os.path.join(settings.TMP_ROOT)

        if not os.path.exists(self.tmp_folder):
            os.makedirs(self.tmp_folder)

    def tearDown(self):
        if os.path.exists(self.tmp_folder):
            shutil.rmtree(self.tmp_folder)

    def test_command_output(self):
        StackedMailEntry.objects.create(receiver='r1@test.com', sender='s1@test.com', title='Title1', content='Body1', is_sent=True)
        StackedMailEntry.objects.create(receiver='r2@test.com', sender='s2@test.com', title='Title2', content='Body2', is_sent=False)
        StackedMailEntry.objects.create(receiver='r3@test.com', sender='s3@test.com', title='Title3', content='Body3', is_sent=False)
        StackedMailEntry.objects.create(receiver='r4@test.com', sender='s4@test.com', title='Title4', content='Body4', is_sent=False)

        MailingController.MailingController.send_stacked_emails()

        mail.outbox.sort(key=lambda x: x.to[0])

        self.assertEqual('r2@test.com', mail.outbox[0].to[0])
        self.assertEqual('s2@test.com', mail.outbox[0].from_email)

        self.assertEqual('r3@test.com', mail.outbox[1].to[0])
        self.assertEqual('s3@test.com', mail.outbox[1].from_email)

        self.assertEqual('r4@test.com', mail.outbox[2].to[0])
        self.assertEqual('s4@test.com', mail.outbox[2].from_email)

        emails = StackedMailEntry.objects.all()

        for email in emails:
            self.assertEqual(True, email.is_sent)

