""" Manager for Bluesteel Layout entries """

from django.db import models
from django.core.paginator import Paginator
from app.service.bluesteel.models.BluesteelCommandModel import BluesteelCommandEntry
from app.service.bluesteel.models.BluesteelCommandSetModel import BluesteelCommandSetEntry
from app.service.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.service.gitrepo.models.GitProjectModel import GitProjectEntry

# pylint: disable=R0904

# Class has not __init__ method
# pylint: disable=W0232

class BluesteelLayoutManager(models.Manager):
    """ Bluesteel Manager """

    @staticmethod
    def create_command(command_set, order, command):
        """ Creates a default command """
        BluesteelCommandEntry.objects.create(
            bluesteel_command_set=command_set,
            order=order,
            command=command
        )

    @staticmethod
    def create_default_command_set_clone(project):
        """ Creates a default command set with CLONE type"""
        command_set_clone = BluesteelCommandSetEntry.objects.create(
            bluesteel_project=project,
            command_set_type=BluesteelCommandSetEntry.CLONE,
        )

        BluesteelLayoutManager.create_command(command_set_clone, 0, 'git clone http://www.test.com')

    @staticmethod
    def create_default_command_set_fetch(project):
        """ Creates a default command set with FETCH type """
        command_set_fetch = BluesteelCommandSetEntry.objects.create(
            bluesteel_project=project,
            command_set_type=BluesteelCommandSetEntry.FETCH,
        )

        BluesteelLayoutManager.create_command(command_set_fetch, 0, 'git checkout master')
        BluesteelLayoutManager.create_command(command_set_fetch, 1, 'git reset --hard origin/master')
        BluesteelLayoutManager.create_command(command_set_fetch, 2, 'git clean -f -d -q')
        BluesteelLayoutManager.create_command(command_set_fetch, 3, 'git pull -r origin master')
        BluesteelLayoutManager.create_command(command_set_fetch, 4, 'git checkout master')
        BluesteelLayoutManager.create_command(command_set_fetch, 5, 'git submodule sync')
        BluesteelLayoutManager.create_command(command_set_fetch, 6, 'git submodule update --init --recursive')

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

    def create_new_default_layout(self):
        """ Create a new default layout with git project and return the ID of it """
        new_layout = self.create(name='default-name')

        new_git_project = GitProjectEntry.objects.create(url='http://www.test.com')

        new_project = BluesteelProjectEntry.objects.create(
            layout=new_layout,
            archive='default-archive',
            name='project-name',
            git_project=new_git_project
        )

        BluesteelLayoutManager.create_default_command_set_clone(new_project)
        BluesteelLayoutManager.create_default_command_set_fetch(new_project)
        return new_layout
