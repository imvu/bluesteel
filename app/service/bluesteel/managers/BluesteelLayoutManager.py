""" Manager for Bluesteel Layout entries """

from django.db import models
from django.core.paginator import Paginator

# pylint: disable=R0904

# Class has not __init__ method
# pylint: disable=W0232

class BluesteelLayoutManager(models.Manager):
    """ Bluesteel Manager """

    @staticmethod
    def add_default_project_to_layout(layout):
        """ Adds a default project to a given layout """
        # I need to fix these function to not have a circular reference :(
        from app.service.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
        project_count = BluesteelProjectEntry.objects.filter(layout=layout).count()
        BluesteelProjectEntry.objects.create_default_project(layout, 'project-name', project_count)


    def get_paginated_layouts_as_objects(self, page):
        """ Returns paginated list of layouts """
        layout_entries = self.all().order_by('-created_at')

        pager = Paginator(layout_entries, page.items_per_page)
        current_page = pager.page(page.page_index)
        layout_entries = current_page.object_list

        layouts = []
        for layout in layout_entries:
            layouts.append(layout.as_object())
        return layouts


    def create_new_default_layout(self):
        """ Create a new default layout with git project and return the ID of it """
        new_layout = self.create(
            name='default-name',
            archive='archive-1'
        )

        BluesteelLayoutManager.add_default_project_to_layout(new_layout)

        return new_layout
