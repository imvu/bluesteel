""" View git repo tests """

from django.test import TestCase
from django.test import Client
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from app.util.httpcommon import res
from app.service.strongholdworker.models.WorkerModel import WorkerEntry
from datetime import timedelta
import json

class ViewsWorkerTestCase(TestCase):

    def setUp(self):
        self.client = Client()

        self.user1 = User.objects.create_user('user1@test.com', 'user1@test.com', 'pass1')

        self.worker_1 = WorkerEntry.objects.create(
            name='worker-1',
            uuid='8a88432d-33db-4d24-a0a7-2f863e7e8e4a',
            description='One Worker :)',
            user=self.user1
        )

    def tearDown(self):
        pass

    def test_get_worker_info(self):
        resp = self.client.get('/bluesteelworker/worker/8a88432d-33db-4d24-a0a7-2f863e7e8e4a/')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual('worker-1', resp_obj['data']['worker']['name'])
        self.assertEqual('8a88432d-33db-4d24-a0a7-2f863e7e8e4a', resp_obj['data']['worker']['uuid'])
        self.assertEqual('One Worker :)', resp_obj['data']['worker']['description'])

    def test_get_worker_info_not_found(self):
        resp = self.client.get('/bluesteelworker/worker/8a88432d-33db-4d24-a0a7-20000000000a/')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(400, resp_obj['status'])
        self.assertEqual('Worker not found', resp_obj['message'])

    def test_create_new_worker_that_does_not_exists_yet(self):
        post_data = {}
        post_data['uuid'] = '8a88432d-33db-4d24-a0a7-000000000000'
        post_data['operative_system'] = 'osx'
        post_data['host_name'] = 'host-name'

        post_str = json.dumps(post_data)

        resp = self.client.post(
            '/bluesteelworker/worker/create/',
            data=post_str,
            content_type='text/plain'
        )

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)


        self.assertEqual(200, resp_obj['status'])
        self.assertEqual('8a88432d-33db-4d24-a0a7-000000000000', resp_obj['data']['uuid'])
        self.assertEqual('osx', resp_obj['data']['operative_system'])
        self.assertEqual('host-name', resp_obj['data']['name'])

        entry = WorkerEntry.objects.all().filter(id=resp_obj['data']['id']).first()

        self.assertEqual('8a88432d-33db-4d24-a0a7-000000000000', entry.uuid)
        self.assertEqual('osx', entry.operative_system)
        self.assertEqual('host-name', entry.name)

        user_entry = User.objects.all().filter(id=entry.user.id).first()

        self.assertEqual('8a88432d-33db-4d24-a0a7-000000', user_entry.username)


    def test_login_worker_with_correct_password(self):
        post_data = {}
        post_data['username'] = '8a88432d-33db-4d24-a0a7-2f863e'
        post_data['password'] = '8a88432d-33db-4d24-a0a7-2f863e7e8e4a'

        user1 = User.objects.create_user(post_data['username'], None, post_data['password'])
        user1.save()

        worker = WorkerEntry.objects.create(
            name='worker-1',
            uuid=post_data['username'],
            description='One Worker :)',
            user=user1
        )

        resp = self.client.post(
            '/bluesteelworker/worker/login/',
            data=json.dumps(post_data),
            content_type='text/plain'
        )

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual('Access granted!', resp_obj['message'])
        self.assertEqual(user1.pk, self.client.session['_auth_user_id'])
        # self.assertEqual(False, self.client.session.has_key('_auth_user_id'))

    def test_login_worker_with_correct_password(self):
        post_data = {}
        post_data['username'] = 'bad-login'
        post_data['password'] = 'bad-password'

        user1 = User.objects.create_user(
            username='8a88432d-33db-4d24-a0a7-2f863e',
            email=None,
            password='8a88432d-33db-4d24-a0a7-2f863e7e8e4a'
        )
        user1.save()

        worker = WorkerEntry.objects.create(
            name='worker-1',
            uuid=post_data['username'],
            description='One Worker :)',
            user=user1
        )

        resp = self.client.post(
            '/bluesteelworker/worker/login/',
            data=json.dumps(post_data),
            content_type='text/plain'
        )

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(401, resp_obj['status'])
        self.assertEqual('Access denied!', resp_obj['message'])
        self.assertEqual(False, self.client.session.has_key('_auth_user_id'))

    def test_update_activity(self):
        update_time_1 = WorkerEntry.objects.filter(id=self.worker_1.id).first().updated_at

        resp = self.client.post(
            '/bluesteelworker/worker/{0}/update/activity/'.format(self.worker_1.id),
            data='',
            content_type='text/plain'
        )

        update_time_2 = WorkerEntry.objects.filter(id=self.worker_1.id).first().updated_at

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertFalse(update_time_1 == update_time_2)
        self.assertTrue(update_time_1 < update_time_2)

