""" Manager for Bluesteel Layout entries """

from django.db import models
from django.core.paginator import Paginator
from app.service.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.service.gitrepo.models.GitProjectModel import GitProjectEntry
from app.util.commandrepo.models.CommandModel import CommandEntry
from app.util.commandrepo.models.CommandSetModel import CommandSetEntry
from app.util.commandrepo.models.CommandGroupModel import CommandGroupEntry

# pylint: disable=R0904

# Class has not __init__ method
# pylint: disable=W0232

class BluesteelLayoutManager(models.Manager):
    """ Bluesteel Manager """

    @staticmethod
    def create_command(command_set, order, command):
        """ Creates a default command """
        command = CommandEntry.objects.create(
            command_set=command_set,
            order=order,
            command=command
        )
        return command

    @staticmethod
    def create_default_command_set_clone(group, order):
        """ Creates a default command set with CLONE type"""
        command_set_clone = CommandSetEntry.objects.create(
            group=group,
            name='CLONE',
            order=order,
        )

        BluesteelLayoutManager.create_command(command_set_clone, 0, 'git clone http://www.test.com')
        return command_set_clone

    @staticmethod
    def create_default_command_set_fetch(group, order):
        """ Creates a default command set with FETCH type """
        command_set_fetch = CommandSetEntry.objects.create(
            group=group,
            name='FETCH',
            order=order,
        )

        BluesteelLayoutManager.create_command(command_set_fetch, 0, 'git checkout master')
        BluesteelLayoutManager.create_command(command_set_fetch, 1, 'git reset --hard origin/master')
        BluesteelLayoutManager.create_command(command_set_fetch, 2, 'git clean -f -d -q')
        BluesteelLayoutManager.create_command(command_set_fetch, 3, 'git fetch --all')
        BluesteelLayoutManager.create_command(command_set_fetch, 4, 'git pull -r origin master')
        BluesteelLayoutManager.create_command(command_set_fetch, 5, 'git checkout master')
        BluesteelLayoutManager.create_command(command_set_fetch, 6, 'git submodule sync')
        BluesteelLayoutManager.create_command(command_set_fetch, 7, 'git submodule update --init --recursive')
        return command_set_fetch

    @staticmethod
    def create_default_command_set_pull(group, order):
        """ Creates a default command set with PULL type"""
        command_set_pull = CommandSetEntry.objects.create(
            group=group,
            name='PULL',
            order=order,
        )

        BluesteelLayoutManager.create_command(command_set_pull, 0, 'git pull -r')
        return command_set_pull

    @staticmethod
    def create_default_command_group():
        """ Creates a group of sets of commands """
        group = CommandGroupEntry.objects.create()
        BluesteelLayoutManager.create_default_command_set_clone(group, 0)
        BluesteelLayoutManager.create_default_command_set_fetch(group, 1)
        BluesteelLayoutManager.create_default_command_set_pull(group, 2)
        return group


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

        new_git_project = GitProjectEntry.objects.create(url='http://www.test.com')

        command_group = BluesteelLayoutManager.create_default_command_group()

        BluesteelProjectEntry.objects.create(
            layout=new_layout,
            name='project-name',
            command_group=command_group,
            git_project=new_git_project
        )

        return new_layout
