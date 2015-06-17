""" Bluesteel Views tests """

from django.test import TestCase
from django.test import Client
from app.service.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.util.httpcommon import res
import json

class BluesteelViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.layout_1 = BluesteelLayoutEntry.objects.create(
            name='layout-1',
            archive='archive-28',
        )

        self.layout_2 = BluesteelLayoutEntry.objects.create(
            name='layout-2',
            archive='archive-28',
        )

        self.layout_3 = BluesteelLayoutEntry.objects.create(
            name='layout-3',
            archive='archive-28',
        )


    def tearDown(self):
        pass

    def test_get_all_layouts_urls(self):
        resp = self.client.get('/bluesteel/layout/all/urls/')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(3, len(resp_obj['data']['layouts']))

        self.assertTrue('http://testserver/bluesteel/layout/1/' in resp_obj['data']['layouts'])
        self.assertTrue('http://testserver/bluesteel/layout/2/' in resp_obj['data']['layouts'])
        self.assertTrue('http://testserver/bluesteel/layout/3/' in resp_obj['data']['layouts'])

    def test_get_layout(self):
        resp = self.client.get('/bluesteel/layout/1/')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(1, resp_obj['data']['id'])
        self.assertEqual('layout-1', resp_obj['data']['name'])
        self.assertEqual('archive-28', resp_obj['data']['archive'])

