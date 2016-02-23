""" Image Catalog tests """

from django.test import TestCase
from django.conf import settings
from app.logic.mailing.models.StackedMailModel import StackedMailEntry
import os
import shutil

class StackedMailTestCase(TestCase):
    def setUp(self):
        self.tmp_folder = os.path.join(settings.TMP_ROOT)

        if not os.path.exists(self.tmp_folder):
            os.makedirs(self.tmp_folder)

    def tearDown(self):
        if os.path.exists(self.tmp_folder):
            shutil.rmtree(self.tmp_folder)

    def test_create_stacked_mail(self):
        self.assertEqual(0, StackedMailEntry.objects.all().count())

        StackedMailEntry.objects.create(
            sender='mail_sender@test.com',
            receiver='mail_receiver@test.com',
            title='Mail Title',
            content='This is the mail content'
        )

        self.assertEqual(1, StackedMailEntry.objects.all().count())
        mail = StackedMailEntry.objects.all()[0]

        self.assertEqual(False, mail.is_sent)

    def test_get_email_as_data(self):
        StackedMailEntry.objects.create(
            sender='mail_sender@test.com',
            receiver='mail_receiver@test.com',
            title='Mail Title',
            content='This is the mail content'
        )

        data = mail = StackedMailEntry.objects.all()[0].get_email_as_data()

        self.assertEqual('Mail Title', data[0])
        self.assertEqual('This is the mail content', data[1])
        self.assertEqual('mail_sender@test.com', data[2])
        self.assertEqual(1, len(data[3]))
        self.assertEqual('mail_receiver@test.com', data[3][0])
