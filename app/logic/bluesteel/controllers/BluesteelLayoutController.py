""" BluesteelLayout Controller file """

from django.core.paginator import Paginator
from app.logic.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.logic.bluesteel.controllers.BluesteelProjectController import BluesteelProjectController
from app.logic.httpcommon import pag

PAGINATION_HALF_RANGE = 2

class BluesteelLayoutController(object):
    """ BluesteelLayout controller with helper functions """

    @staticmethod
    def add_default_project_to_layout(layout):
        """ Adds a default project to a given layout """
        project_count = BluesteelProjectEntry.objects.filter(layout=layout).count()
        BluesteelProjectController.create_default_project(layout, 'project-name', project_count)

    @staticmethod
    def sort_layout_projects_by_order(layout):
        """ Sorts all projects on a layout by order """
        project_entries = BluesteelProjectEntry.objects.filter(layout=layout)

        for index, project in enumerate(project_entries):
            project.order = index
            project.save()

    @staticmethod
    def get_paginated_layouts_as_objects(page):
        """ Returns paginated list of layouts """
        layout_entries = BluesteelLayoutEntry.objects.all().order_by('-created_at')

        pager = Paginator(layout_entries, page.items_per_page)
        current_page = pager.page(page.page_index)
        layout_entries = current_page.object_list
        page_indices = pag.get_pagination_indices(page, PAGINATION_HALF_RANGE, pager.num_pages)

        layouts = []
        for layout in layout_entries:
            layouts.append(layout.as_object())
        return (layouts, page_indices)

    @staticmethod
    def create_new_default_layout():
        """ Create a new default layout with git project and return the ID of it """
        new_layout = BluesteelLayoutEntry.objects.create(
            name='default-name',
        )

        BluesteelLayoutController.add_default_project_to_layout(new_layout)

        return new_layout

    @staticmethod
    def delete_layout(layout):
        """ Delete layout """
        project_entries = BluesteelProjectEntry.objects.filter(layout=layout)

        for project in project_entries:
            BluesteelProjectController.delete_project(project)
        layout.delete()


    @staticmethod
    def get_project_names_of_layout(layout_id):
        """ Returns a list of names with id of the projects inside a layout """
        project_entries = BluesteelProjectEntry.objects.filter(layout_id=layout_id).values('id', 'name').order_by('id')

        projects = []
        for entry in project_entries:
            obj = {}
            obj['name'] = entry['name']
            obj['id'] = entry['id']
            projects.append(obj)

        return projects
