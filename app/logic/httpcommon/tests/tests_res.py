""" Res tests """

from django.test import TestCase
from django.http import HttpResponse
from app.logic.httpcommon import res
import json


# Create your tests here.

class ViewResTestCase(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_add_headers(self):
        http_req = {}

        res.add_cross_origin_properties(http_req)

        self.assertEqual(http_req["Access-Control-Allow-Origin"], "*")
        self.assertEqual(http_req["Access-Control-Allow-Methods"], "POST, GET, OPTIONS")
        self.assertEqual(http_req["Access-Control-Max-Age"], "1000")
        self.assertEqual(http_req["Access-Control-Allow-Headers"], "*")

    def test_get_response(self):
        resp = res.get_response(200, 'msg1', {'key1' : 'val1'})

        self.assertEqual(resp["Access-Control-Allow-Origin"], "*")
        self.assertEqual(resp["Access-Control-Allow-Methods"], "POST, GET, OPTIONS")
        self.assertEqual(resp["Access-Control-Max-Age"], "1000")
        self.assertEqual(resp["Access-Control-Allow-Headers"], "*")

        obj = json.loads(resp.content)
        self.assertEqual(obj['status'], 200)
        self.assertEqual(obj['message'], 'msg1')
        self.assertEqual(obj['data']['key1'], 'val1')

