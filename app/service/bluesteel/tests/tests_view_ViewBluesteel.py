""" Bluesteel View tests """

from django.test import TestCase
from django.test import Client
from app.service.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.service.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.service.bluesteel.models.BluesteelCommandSetModel import BluesteelCommandSetEntry
from app.service.gitrepo.models.GitProjectModel import GitProjectEntry
from app.util.httpcommon import res
import json

class BluesteelProjectTestCase(TestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_post_creates_default_layout(self):
        resp = self.client.post('/bluesteel/layout/create/', {})
        res.check_cross_origin_headers(self, resp)
        resp_json = json.loads(resp.content)

        new_layout = BluesteelLayoutEntry.objects.all().first()

        self.assertEqual(200, resp_json['status'])
        self.assertEqual('New layout created', resp_json['message'])
        self.assertEqual(new_layout.id, resp_json['data']['layout']['id'])
        self.assertEqual(new_layout.name, resp_json['data']['layout']['name'])

    def test_post_creates_default_layout_fails_because_get(self):
        resp = self.client.get('/bluesteel/layout/create/')
        res.check_cross_origin_headers(self, resp)
        resp_json = json.loads(resp.content)

        new_layout = BluesteelLayoutEntry.objects.all().first()

        self.assertEqual(None, new_layout)
        self.assertEqual(400, resp_json['status'])