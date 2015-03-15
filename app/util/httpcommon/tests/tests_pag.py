""" Pag tests """

from django.test import TestCase
from django.http import HttpResponse
from app.util.httpcommon import pag
import json


# Create your tests here.

class ViewPagTestCase(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_pagination_out_of_bounds_elements_zero(self):
        self.assertEqual(True, pag.is_pagination_out_of_bounds([], 3, 1))

    def test_pagination_out_of_bounds_items_per_page_zero(self):
        self.assertEqual(True, pag.is_pagination_out_of_bounds([1,2,3,4], 0, 1))

    def test_pagination_out_of_bounds_page_index_zero(self):
        self.assertEqual(True, pag.is_pagination_out_of_bounds([1,2,3,4], 3, 0))

    def test_pagination_out_of_bounds_page_index_greater_than_pages(self):
        self.assertEqual(True, pag.is_pagination_out_of_bounds([1,2,3,4], 3, 25))

    def test_pagination_out_of_bounds_correct(self):
        self.assertEqual(False, pag.is_pagination_out_of_bounds([1,2,3,4], 3, 1))

    def test_pagination_normal_range(self):
        element_list = range(15)

        page_link_list = pag.get_navigation_links(
            element_list=element_list,
            items_per_page=2,
            page_index=3,
            page_link_count=3,
            url='/view/main/'
        )

        self.assertEqual('/view/main/page/2/2/dots/3/', page_link_list['prev'])
        self.assertEqual('/view/main/page/2/2/dots/3/', page_link_list['pages'][0]['url'])
        self.assertEqual(2, page_link_list['pages'][0]['index'])
        self.assertEqual('', page_link_list['pages'][1]['url'])
        self.assertEqual(3, page_link_list['pages'][1]['index'])
        self.assertEqual('/view/main/page/2/4/dots/3/', page_link_list['pages'][2]['url'])
        self.assertEqual(4, page_link_list['pages'][2]['index'])
        self.assertEqual('/view/main/page/2/4/dots/3/', page_link_list['next'])

    def test_pagination_range_clamped_on_zero(self):
        element_list = range(15)

        page_link_list = pag.get_navigation_links(
            element_list=element_list,
            items_per_page=1,
            page_index=1,
            page_link_count=3,
            url='/view/main/'
        )

        self.assertEqual('', page_link_list['prev'])
        self.assertEqual('', page_link_list['pages'][0]['url'])
        self.assertEqual(1, page_link_list['pages'][0]['index'])
        self.assertEqual('/view/main/page/1/2/dots/3/', page_link_list['pages'][1]['url'])
        self.assertEqual(2, page_link_list['pages'][1]['index'])
        self.assertEqual('/view/main/page/1/3/dots/3/', page_link_list['pages'][2]['url'])
        self.assertEqual(3, page_link_list['pages'][2]['index'])
        self.assertEqual('/view/main/page/1/2/dots/3/', page_link_list['next'])

    def test_pagination_range_clamped_on_max_pages(self):
        element_list = range(6)

        page_link_list = pag.get_navigation_links(
            element_list=element_list,
            items_per_page=1,
            page_index=6,
            page_link_count=3,
            url='/view/main/'
        )

        self.assertEqual('/view/main/page/1/5/dots/3/', page_link_list['prev'])
        self.assertEqual('/view/main/page/1/4/dots/3/', page_link_list['pages'][0]['url'])
        self.assertEqual(4, page_link_list['pages'][0]['index'])
        self.assertEqual('/view/main/page/1/5/dots/3/', page_link_list['pages'][1]['url'])
        self.assertEqual(5, page_link_list['pages'][1]['index'])
        self.assertEqual('', page_link_list['pages'][2]['url'])
        self.assertEqual(6, page_link_list['pages'][2]['index'])
        self.assertEqual('', page_link_list['next'])

    def test_pagination_range_out_of_bounds_zero(self):
        element_list = range(15)

        page_link_list = pag.get_navigation_links(
            element_list=element_list,
            items_per_page=1,
            page_index=0,
            page_link_count=3,
            url='/view/main/'
        )

        self.assertEqual(0, len(page_link_list['pages']))
        self.assertEqual('', page_link_list['next'])
        self.assertEqual('', page_link_list['prev'])

    def test_pagination_range_out_of_bounds_max(self):
        element_list = range(6)

        page_link_list = pag.get_navigation_links(
            element_list=element_list,
            items_per_page=1,
            page_index=8,
            page_link_count=3,
            url='/view/main/'
        )

        self.assertEqual(0, len(page_link_list['pages']))
        self.assertEqual('', page_link_list['next'])
        self.assertEqual('', page_link_list['prev'])

    def test_pagination_page_link_count_greater_than_len_items(self):
        element_list = range(3)

        page_link_list = pag.get_navigation_links(
            element_list=element_list,
            items_per_page=1,
            page_index=1,
            page_link_count=5,
            url='/view/main/'
        )

        self.assertEqual(3, len(page_link_list['pages']))
        self.assertEqual('/view/main/page/1/2/dots/5/', page_link_list['next'])
        self.assertEqual('', page_link_list['prev'])
        self.assertEqual('', page_link_list['pages'][0]['url'])
        self.assertEqual(1, page_link_list['pages'][0]['index'])
        self.assertEqual('/view/main/page/1/2/dots/5/', page_link_list['pages'][1]['url'])
        self.assertEqual(2, page_link_list['pages'][1]['index'])
        self.assertEqual('/view/main/page/1/3/dots/5/', page_link_list['pages'][2]['url'])
        self.assertEqual(3, page_link_list['pages'][2]['index'])

