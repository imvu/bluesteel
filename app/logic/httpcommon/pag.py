""" Common code for pagination """

from django.core.paginator import Paginator
from app.logic.httpcommon.Page import Page

def is_pagination_out_of_bounds(element_list, page):
    """ Checks if pagination info is out of bounds """
    if len(element_list) == 0:
        return True

    if page.items_per_page < 1:
        return True

    pager = Paginator(element_list, page.items_per_page)

    if (page.page_index < 1) or (page.page_index > pager.num_pages):
        return True
    return False

def get_empty_navigation_obj():
    """ Returns a default-empty navigation object """
    pagination_obj = {}
    pagination_obj['next'] = ''
    pagination_obj['prev'] = ''
    pagination_obj['pages'] = []
    return pagination_obj

def get_navigation_links(element_list, page, page_link_count, url):
    """ Returns a list of pages to navigate from current page """
    page_link_count = int(page_link_count)

    pagination_obj = get_empty_navigation_obj()

    if is_pagination_out_of_bounds(element_list, page):
        return pagination_obj

    pager = Paginator(element_list, page.items_per_page)
    half_range = int(page_link_count / 2)
    page_index_start = 0
    page_index_end = 0
    if (page.page_index - half_range) < 1:
        page_index_start = 1
        page_index_end = page_index_start + min((page_link_count - 1), pager.num_pages)
    elif page.page_index + half_range > pager.num_pages:
        page_index_start = max(1, pager.num_pages - (page_link_count - 1))
        page_index_end = pager.num_pages
    else:
        page_index_start = page.page_index - half_range
        page_index_end = page.page_index + half_range

    page_range = pager.page_range[page_index_start - 1:page_index_end]

    page_info_list = []
    for index in page_range:
        page_info = {}
        page_info['index'] = index
        if index == page.page_index:
            page_info['url'] = ''
        else:
            tmp_page = Page(page.items_per_page, index)
            page_info['url'] = append_pag_info(url, tmp_page, page_link_count)
        page_info_list.append(page_info)

    current_page = pager.page(page.page_index)

    if current_page.has_previous():
        tmp_page = Page(page.items_per_page, current_page.previous_page_number())
        pagination_obj['prev'] = append_pag_info(
            url,
            tmp_page,
            page_link_count
        )

    if current_page.has_next():
        tmp_page = Page(page.items_per_page, current_page.next_page_number())
        pagination_obj['next'] = append_pag_info(url, tmp_page, page_link_count)

    pagination_obj['pages'] = page_info_list

    return pagination_obj

def append_pag_info(url, page, dot_count):
    return '{0}page/{1}/{2}/dots/{3}/'.format(url, page.items_per_page, page.page_index, dot_count)
