""" Presenter Views tests """

from django.test import TestCase
from django.test import Client
from app.service.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.util.httpcommon import res
import json

class BluesteelViewLayoutTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.layout_1 = BluesteelLayoutEntry.objects.create(
            name='layout-1',
            archive='archive-28',
            collect_commits_path='/original/url/',
        )

    def tearDown(self):
        pass

    def test_save_bluesteel_layout(self):
        obj = {}
        obj['name'] = 'layout-1'
        obj['collect_commits_path'] = '/changed/url/'

        self.assertEqual(1, BluesteelLayoutEntry.objects.filter(name='layout-1', collect_commits_path='/original/url/').count())

        resp = self.client.post(
            '/main/layout/{0}/save/'.format(self.layout_1.id),
            data = json.dumps(obj),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual(1, BluesteelLayoutEntry.objects.filter(name='layout-1', collect_commits_path='/changed/url/').count())

