""" View git repo tests """

from django.test import TestCase
from django.test import Client
from django.conf import settings
from django.utils import timezone
from app.util.httpcommon import res
from app.service.strongholdworker.models.WorkerModel import WorkerEntry
from datetime import timedelta
import json

class ViewsWorkerTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.worker_1 = WorkerEntry.objects.create(
            name='worker-1',
            uuid='8a88432d-33db-4d24-a0a7-2f863e7e8e4a',
            description='One Worker :)'
        )

    def tearDown(self):
        pass

    def test_get_worker_info(self):
        resp = self.client.get('/bluesteelworker/worker/8a88432d-33db-4d24-a0a7-2f863e7e8e4a/')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual('worker-1', resp_obj['data']['name'])
        self.assertEqual('8a88432d-33db-4d24-a0a7-2f863e7e8e4a', resp_obj['data']['uuid'])
        self.assertEqual('One Worker :)', resp_obj['data']['description'])

    def test_get_worker_info_not_found(self):
        resp = self.client.get('/bluesteelworker/worker/8a88432d-33db-4d24-a0a7-20000000000a/')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(400, resp_obj['status'])
        self.assertEqual('Worker not found', resp_obj['message'])
