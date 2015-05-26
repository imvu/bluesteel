""" Manager for Bluesteel Layout entries """

from django.db import models
from django.core.paginator import Paginator

# pylint: disable=R0904

# Class has not __init__ method
# pylint: disable=W0232

class BluesteelLayoutManager(models.Manager):
    """ Bluesteel Manager """

    def get_paginated_layouts_as_objects(self, page):
        """ Returns paginated list of layouts """
        layout_entries = self.all()

        pager = Paginator(layout_entries, page.items_per_page)
        current_page = pager.page(page.page_index)
        layout_entries = current_page.object_list

        layouts = []
        for layout in layout_entries:
            layouts.append(layout.as_object())
        return layouts

