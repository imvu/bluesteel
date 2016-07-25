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

    def create_stacked_email(self, sender, receiver, title, msg, sent):
        StackedMailEntry.objects.create(
            receiver=receiver,
            sender=sender,
            title=title,
            content=msg,
            is_sent=sent
        )

    def test_command_output(self):
        self.create_stacked_email('s1@test.com', 'r1@test.com', 'Title1', 'Body1', True)
        self.create_stacked_email('s2@test.com', 'r2@test.com', 'Title2', 'Body2', False)
        self.create_stacked_email('s3@test.com', 'r3@test.com', 'Title3', 'Body3', False)
        self.create_stacked_email('s4@test.com', 'r4@test.com', 'Title4', 'Body4', False)

        StackedMailEntry.objects.create(receiver='s1@test.com', sender='r1@test.com', title='Title1', content='Body1', is_sent=True)
        StackedMailEntry.objects.create(receiver='s2@test.com', sender='r2@test.com', title='Title2', content='Body2', is_sent=False)
        StackedMailEntry.objects.create(receiver='s3@test.com', sender='r3@test.com', title='Title3', content='Body3', is_sent=False)
        StackedMailEntry.objects.create(receiver='s4@test.com', sender='r4@test.com', title='Title4', content='Body4', is_sent=False)

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

