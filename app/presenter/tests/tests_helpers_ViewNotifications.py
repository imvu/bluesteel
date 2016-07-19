""" Helper notification tests """

from django.test import TestCase
from django.contrib.auth.models import User, Group
from app.presenter.views.helpers import ViewNotifications
from app.logic.mailing.models.StackedMailModel import StackedMailEntry

class NotificationHelperTestCase(TestCase):

    def setUp(self):
        self.group1 = Group.objects.create(name='Group1')
        self.group2 = Group.objects.create(name='admin')

        self.user1 = User.objects.create_user('user1@test.com', 'user1@test.com', 'pass1')
        self.user2 = User.objects.create_user('user2@test.com', 'user2@test.com', 'pass2')
        self.user3 = User.objects.create_user('user3@test.com', 'user3@test.com', 'pass3')

        self.user1.groups.add(self.group1)
        self.user2.groups.add(self.group2)

    def tearDown(self):
        pass

    def test_notifiying_only_receiver(self):
        self.assertEqual(0, StackedMailEntry.objects.all().count())

        ViewNotifications.create_notification_email('a@b.c', 'title1', 'content1', [])

        self.assertEqual(1, StackedMailEntry.objects.all().count())
        self.assertEqual(1, StackedMailEntry.objects.filter(sender='bluesteel@bluesteel.com', receiver='a@b.c', title='title1', content='content1').count())

    def test_notifiying_to_receiver_and_group_admin(self):
        self.assertEqual(0, StackedMailEntry.objects.all().count())

        ViewNotifications.create_notification_email('a@b.c', 'title1', 'content1', ['admin'])

        self.assertEqual(2, StackedMailEntry.objects.all().count())
        self.assertEqual(1, StackedMailEntry.objects.filter(sender='bluesteel@bluesteel.com', receiver='a@b.c', title='title1', content='content1').count())
        self.assertEqual(1, StackedMailEntry.objects.filter(sender='bluesteel@bluesteel.com', receiver='user2@test.com', title='title1', content='content1').count())

    def test_notifiying_to_receiver_and_all_groups(self):
        self.assertEqual(0, StackedMailEntry.objects.all().count())

        ViewNotifications.create_notification_email('a@b.c', 'title1', 'content1', ['admin', 'Group1'])

        self.assertEqual(3, StackedMailEntry.objects.all().count())
        self.assertEqual(1, StackedMailEntry.objects.filter(sender='bluesteel@bluesteel.com', receiver='a@b.c', title='title1', content='content1').count())
        self.assertEqual(1, StackedMailEntry.objects.filter(sender='bluesteel@bluesteel.com', receiver='user2@test.com', title='title1', content='content1').count())
        self.assertEqual(1, StackedMailEntry.objects.filter(sender='bluesteel@bluesteel.com', receiver='user1@test.com', title='title1', content='content1').count())
