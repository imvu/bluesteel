""" Common code for pagination """

def get_pagination_indices(page, half_range, maximum_pages):
    """ Returns all the pagination indices """

    max_pages = max(1, maximum_pages)
    current_page = min(max(1, page.page_index), max_pages)
    start_range = max(1, page.page_index - half_range)
    whole_range = min(max_pages, (int(half_range) * 2) + 1)

    if (page.page_index - half_range) < 1:
        start_range = max(1, page.page_index - half_range)

    if page.page_index + half_range > max_pages:
        start_range = max(1, max_pages - (whole_range - 1))

    pagination = {}
    pagination['prev'] = max(1, current_page - 1)
    pagination['current'] = current_page
    pagination['next'] = min(max_pages, current_page + 1)
    pagination['page_indices'] = range(start_range, start_range + whole_range)
    return pagination

def get_pagination_urls(pagination, url):
    """ Return a pagination object with urls """

    pag_url = {}
    pag_url['prev'] = '{0}page/{1}/'.format(url, pagination['prev'])
    pag_url['current'] = '{0}page/{1}/'.format(url, pagination['current'])
    pag_url['next'] = '{0}page/{1}/'.format(url, pagination['next'])
    pag_url['pages'] = []

    for page_index in pagination['page_indices']:
        pag = {}
        pag['url'] = '{0}page/{1}/'.format(url, page_index)
        pag['index'] = page_index
        pag['is_current'] = page_index == pagination['current']
        pag_url['pages'].append(pag)

    return pag_url
