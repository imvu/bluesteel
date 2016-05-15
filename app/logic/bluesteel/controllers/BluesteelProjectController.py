""" BluesteelProject Controller file """

from django.core.paginator import Paginator
from app.logic.httpcommon import pag
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.logic.gitrepo.models.GitProjectModel import GitProjectEntry
from app.logic.gitrepo.controllers.GitController import GitController
from app.logic.commandrepo.models.CommandModel import CommandEntry
from app.logic.commandrepo.models.CommandSetModel import CommandSetEntry
from app.logic.commandrepo.models.CommandGroupModel import CommandGroupEntry
from app.logic.commandrepo.controllers.CommandController import CommandController

PAGINATION_HALF_RANGE = 2

class BluesteelProjectController(object):
    """ BluesteelProject controller with helper functions """

    @staticmethod
    def get_paginated_projects_as_objects(page):
        """ Returns paginated list of projects """
        project_entries = BluesteelProjectEntry.objects.all().order_by('-created_at')

        pager = Paginator(project_entries, page.items_per_page)
        current_page = pager.page(page.page_index)
        project_entries = current_page.object_list
        page_indices = pag.get_pagination_indices(page, PAGINATION_HALF_RANGE, pager.num_pages)

        projects = []
        for project in project_entries:
            projects.append(project.as_object())
        return (projects, page_indices)

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

        BluesteelProjectController.create_command(command_set_clone, 0, 'git clone http://www.test.com')
        return command_set_clone

    @staticmethod
    def create_default_command_set_fetch(group, order):
        """ Creates a default command set with FETCH type """
        command_set_fetch = CommandSetEntry.objects.create(
            group=group,
            name='FETCH',
            order=order,
        )

        BluesteelProjectController.create_command(command_set_fetch, 0, 'git reset HEAD')
        BluesteelProjectController.create_command(command_set_fetch, 1, 'git checkout -- .')
        BluesteelProjectController.create_command(command_set_fetch, 2, 'git clean -d -f -q')
        BluesteelProjectController.create_command(command_set_fetch, 3, 'git submodule sync --recursive')
        BluesteelProjectController.create_command(
            command_set_fetch,
            4,
            'git submodule update --init --recursive --force')
        BluesteelProjectController.create_command(command_set_fetch, 5, 'git checkout master')
        BluesteelProjectController.create_command(command_set_fetch, 6, 'git reset --hard origin/master')
        BluesteelProjectController.create_command(command_set_fetch, 7, 'git clean -d -f -q')
        BluesteelProjectController.create_command(command_set_fetch, 8, 'git fetch --all -p')
        BluesteelProjectController.create_command(command_set_fetch, 9, 'git pull -r origin master')
        BluesteelProjectController.create_command(command_set_fetch, 10, 'git checkout master')
        BluesteelProjectController.create_command(command_set_fetch, 11, 'git submodule sync --recursive')
        BluesteelProjectController.create_command(
            command_set_fetch,
            12,
            'git submodule update --init --recursive --force')
        return command_set_fetch

    @staticmethod
    def create_default_command_set_pull(group, order):
        """ Creates a default command set with PULL type"""
        command_set_pull = CommandSetEntry.objects.create(
            group=group,
            name='PULL',
            order=order,
        )

        BluesteelProjectController.create_command(command_set_pull, 0, 'git pull -r')
        return command_set_pull

    @staticmethod
    def create_default_command_group():
        """ Creates a group of sets of commands """
        group = CommandGroupEntry.objects.create()
        BluesteelProjectController.create_default_command_set_clone(group, 0)
        BluesteelProjectController.create_default_command_set_fetch(group, 1)
        return group

    @staticmethod
    def delete_project(project):
        CommandController.delete_command_group_by_id(project.command_group.id)
        GitController.delete_git_project(project.git_project)
        project.delete()

    @staticmethod
    def create_default_project(layout, name, order):
        """ Adds a default project to a given layout """
        new_git_project = GitProjectEntry.objects.create(url='http://www.test.com')

        command_group = BluesteelProjectController.create_default_command_group()

        entry = BluesteelProjectEntry.objects.create(
            layout=layout,
            name=name,
            order=order,
            command_group=command_group,
            git_project=new_git_project
        )

        return entry

    @staticmethod
    def get_project_git_branch_data(page, project, commit_depth):
        """ Returns branch data associated with a project """
        return GitController.get_pgtd_branches_trimmed_by_merge_target(page, project, commit_depth)


    @staticmethod
    def get_project_single_git_branch_data(project, branch, commit_depth):
        """ Returns a single branch data associated with a project """
        return GitController.get_single_branch_trimmed_by_merge_target(project, branch, commit_depth)
