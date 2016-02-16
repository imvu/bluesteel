""" Trans tests """

from django.test import TestCase
from app.logic.httpcommon import trans
from datetime import datetime

class ViewResTestCase(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_trans_datetime(self):
        http_req = {}

        date_tmp = datetime(1982, 3, 28, 20, 1, 3, 29)

        obj = trans.to_date_obj(date_tmp)

        self.assertEqual(1982, obj['year'])
        self.assertEqual(3, obj['month'])
        self.assertEqual(28, obj['day'])
        self.assertEqual(20, obj['hour'])
        self.assertEqual(1, obj['minute'])
        self.assertEqual(3, obj['second'])
        self.assertEqual(29, obj['microsecond'])
        self.assertEqual('None', obj['tzinfo'])


