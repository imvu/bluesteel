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

    def test_notifying_on_command_failure(self):
        self.assertEqual(0, StackedMailEntry.objects.all().count())

        com1 = {}
        com1['command'] = 'command-1'
        com1['result'] = {}
        com1['result']['status'] = 0
        com1['result']['out'] = 'out-1'
        com1['result']['error'] = 'error-1'

        com2 = {}
        com2['command'] = 'command-2'
        com2['result'] = {}
        com2['result']['status'] = -1
        com2['result']['out'] = 'out-2'
        com2['result']['error'] = 'error-2'

        report_json = {}
        report_json['command_set'] = []
        report_json['command_set'].append(com1)
        report_json['command_set'].append(com2)

        ViewNotifications.notify_benchmark_command_failure(28, 'a@b.c', '0000100001000010000100001000010000100001', report_json, 'test.com')

        self.assertEqual(2, StackedMailEntry.objects.all().count())
        self.assertEqual(1, StackedMailEntry.objects.filter(sender='bluesteel@bluesteel.com', receiver='a@b.c').count())
        self.assertEqual(1, StackedMailEntry.objects.filter(sender='bluesteel@bluesteel.com', receiver='user2@test.com').count())
        self.assertTrue('http://test.com/main/execution/28/complete/' in StackedMailEntry.objects.filter(sender='bluesteel@bluesteel.com', receiver='a@b.c').first().content)
        self.assertTrue('command-1' in StackedMailEntry.objects.filter(sender='bluesteel@bluesteel.com', receiver='a@b.c').first().content)
        self.assertTrue('out-1' in StackedMailEntry.objects.filter(sender='bluesteel@bluesteel.com', receiver='a@b.c').first().content)
        self.assertTrue('error-1' in StackedMailEntry.objects.filter(sender='bluesteel@bluesteel.com', receiver='a@b.c').first().content)
        self.assertTrue('command-2' in StackedMailEntry.objects.filter(sender='bluesteel@bluesteel.com', receiver='a@b.c').first().content)
        self.assertTrue('out-2' in StackedMailEntry.objects.filter(sender='bluesteel@bluesteel.com', receiver='a@b.c').first().content)
        self.assertTrue('error-2' in StackedMailEntry.objects.filter(sender='bluesteel@bluesteel.com', receiver='a@b.c').first().content)

        self.assertTrue('http://test.com/main/execution/28/complete/' in StackedMailEntry.objects.filter(sender='bluesteel@bluesteel.com', receiver='user2@test.com').first().content)
        self.assertTrue('command-1' in StackedMailEntry.objects.filter(sender='bluesteel@bluesteel.com', receiver='user2@test.com').first().content)
        self.assertTrue('out-1' in StackedMailEntry.objects.filter(sender='bluesteel@bluesteel.com', receiver='user2@test.com').first().content)
        self.assertTrue('error-1' in StackedMailEntry.objects.filter(sender='bluesteel@bluesteel.com', receiver='user2@test.com').first().content)
        self.assertTrue('command-2' in StackedMailEntry.objects.filter(sender='bluesteel@bluesteel.com', receiver='user2@test.com').first().content)
        self.assertTrue('out-2' in StackedMailEntry.objects.filter(sender='bluesteel@bluesteel.com', receiver='user2@test.com').first().content)
        self.assertTrue('error-2' in StackedMailEntry.objects.filter(sender='bluesteel@bluesteel.com', receiver='user2@test.com').first().content)

    def test_notifying_on_schema_failure(self):
        self.assertEqual(0, StackedMailEntry.objects.all().count())

        ViewNotifications.notify_schema_failed('a@b.c', 'message-1-1-1-1', 'schema-1-1-1-1')

        self.assertEqual(2, StackedMailEntry.objects.all().count())
        self.assertEqual(1, StackedMailEntry.objects.filter(sender='bluesteel@bluesteel.com', receiver='a@b.c').count())
        self.assertEqual(1, StackedMailEntry.objects.filter(sender='bluesteel@bluesteel.com', receiver='user2@test.com').count())
        self.assertTrue('message-1-1-1-1' in StackedMailEntry.objects.filter(sender='bluesteel@bluesteel.com', receiver='a@b.c').first().content)
        self.assertTrue('schema-1-1-1-1' in StackedMailEntry.objects.filter(sender='bluesteel@bluesteel.com', receiver='a@b.c').first().content)
        self.assertTrue('message-1-1-1-1' in StackedMailEntry.objects.filter(sender='bluesteel@bluesteel.com', receiver='user2@test.com').first().content)
        self.assertTrue('schema-1-1-1-1' in StackedMailEntry.objects.filter(sender='bluesteel@bluesteel.com', receiver='user2@test.com').first().content)

    def test_notifying_on_json_failure(self):
        self.assertEqual(0, StackedMailEntry.objects.all().count())

        ViewNotifications.notify_json_invalid('a@b.c', 'message-1-1-1-1')

        self.assertEqual(2, StackedMailEntry.objects.all().count())
        self.assertEqual(1, StackedMailEntry.objects.filter(sender='bluesteel@bluesteel.com', receiver='a@b.c').count())
        self.assertEqual(1, StackedMailEntry.objects.filter(sender='bluesteel@bluesteel.com', receiver='user2@test.com').count())
        self.assertTrue('message-1-1-1-1' in StackedMailEntry.objects.filter(sender='bluesteel@bluesteel.com', receiver='a@b.c').first().content)
        self.assertTrue('message-1-1-1-1' in StackedMailEntry.objects.filter(sender='bluesteel@bluesteel.com', receiver='user2@test.com').first().content)
