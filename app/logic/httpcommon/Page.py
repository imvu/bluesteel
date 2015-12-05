""" Page object file """

class Page(object):
    """ Page object, it contains information about the pare we are refering, index, items per page, etc. """

    page_index = 0
    items_per_page = 0

    def __init__(self, items_per_page, page_index):
        """ Creates the page """
        self.page_index = int(page_index)
        self.items_per_page = int(items_per_page)
