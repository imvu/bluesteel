""" Pag tests """

from django.test import TestCase
from django.http import HttpResponse
from app.logic.httpcommon import pag
from app.logic.httpcommon.Page import Page
import json


# Create your tests here.

class ViewPagTestCase(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_pagination_indices_start_out_of_bounds(self):
        pagination = pag.get_pagination_indices(Page(1, 2), 2, 10)

        self.assertEqual(1, pagination['prev'])
        self.assertEqual(2, pagination['current'])
        self.assertEqual(3, pagination['next'])
        self.assertEqual([1,2,3,4,5], pagination['page_indices'])

    def test_pagination_indices_start_inbounds(self):
        pagination = pag.get_pagination_indices(Page(1, 4), 2, 10)

        self.assertEqual(3, pagination['prev'])
        self.assertEqual(4, pagination['current'])
        self.assertEqual(5, pagination['next'])
        self.assertEqual([2,3,4,5,6], pagination['page_indices'])

    def test_pagination_indices_start_close_to_upper_bound(self):
        pagination = pag.get_pagination_indices(Page(1, 9), 2, 10)

        self.assertEqual(8, pagination['prev'])
        self.assertEqual(9, pagination['current'])
        self.assertEqual(10, pagination['next'])
        self.assertEqual([6,7,8,9,10], pagination['page_indices'])

    def test_pagination_indices_start_out_of_bounds_small(self):
        pagination = pag.get_pagination_indices(Page(1, 2), 2, 4)

        self.assertEqual(1, pagination['prev'])
        self.assertEqual(2, pagination['current'])
        self.assertEqual(3, pagination['next'])
        self.assertEqual([1,2,3,4], pagination['page_indices'])

    def test_pagination_indices_start_close_to_upper_bounds_small(self):
        pagination = pag.get_pagination_indices(Page(1, 3), 2, 4)

        self.assertEqual(2, pagination['prev'])
        self.assertEqual(3, pagination['current'])
        self.assertEqual(4, pagination['next'])
        self.assertEqual([1,2,3,4], pagination['page_indices'])

    def test_pagination_indices_only_one_page(self):
        pagination = pag.get_pagination_indices(Page(1, 3), 2, 1)

        self.assertEqual(1, pagination['prev'])
        self.assertEqual(1, pagination['current'])
        self.assertEqual(1, pagination['next'])
        self.assertEqual([1], pagination['page_indices'])

    def test_pagination_page_index_out_upper_bound(self):
        pagination = pag.get_pagination_indices(Page(1, 12), 2, 10)

        self.assertEqual(9, pagination['prev'])
        self.assertEqual(10, pagination['current'])
        self.assertEqual(10, pagination['next'])
        self.assertEqual([6,7,8,9,10], pagination['page_indices'])

    def test_pagination_page_index_out_bottom_bound(self):
        pagination = pag.get_pagination_indices(Page(1, -1), 2, 10)

        self.assertEqual(1, pagination['prev'])
        self.assertEqual(1, pagination['current'])
        self.assertEqual(2, pagination['next'])
        self.assertEqual([1,2,3,4,5], pagination['page_indices'])

    def test_pagination_normal_range(self):
        pagination = pag.get_pagination_indices(Page(2, 3), 2, 15)
        pag_url = pag.get_pagination_urls(pagination, '/view/main/')

        self.assertEqual('/view/main/page/2/', pag_url['prev'])
        self.assertEqual('/view/main/page/3/', pag_url['current'])
        self.assertEqual('/view/main/page/4/', pag_url['next'])
        self.assertEqual('/view/main/page/1/', pag_url['pages'][0]['url'])
        self.assertEqual('/view/main/page/2/', pag_url['pages'][1]['url'])
        self.assertEqual('/view/main/page/3/', pag_url['pages'][2]['url'])
        self.assertEqual('/view/main/page/4/', pag_url['pages'][3]['url'])
        self.assertEqual('/view/main/page/5/', pag_url['pages'][4]['url'])
        self.assertEqual(1, pag_url['pages'][0]['index'])
        self.assertEqual(2, pag_url['pages'][1]['index'])
        self.assertEqual(3, pag_url['pages'][2]['index'])
        self.assertEqual(4, pag_url['pages'][3]['index'])
        self.assertEqual(5, pag_url['pages'][4]['index'])
        self.assertEqual(False, pag_url['pages'][0]['is_current'])
        self.assertEqual(False, pag_url['pages'][1]['is_current'])
        self.assertEqual(True,  pag_url['pages'][2]['is_current'])
        self.assertEqual(False, pag_url['pages'][3]['is_current'])
        self.assertEqual(False, pag_url['pages'][4]['is_current'])
