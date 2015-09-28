""" BluesteelProject Controller file """

from app.service.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.service.gitrepo.models.GitProjectModel import GitProjectEntry
from app.service.gitrepo.controllers.GitController import GitController
from app.util.commandrepo.models.CommandModel import CommandEntry
from app.util.commandrepo.models.CommandSetModel import CommandSetEntry
from app.util.commandrepo.models.CommandGroupModel import CommandGroupEntry

class BluesteelProjectController(object):
    """ BluesteelProject controller with helper functions """

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

        BluesteelProjectController.create_command(command_set_fetch, 0, 'git checkout master')
        BluesteelProjectController.create_command(command_set_fetch, 1, 'git reset --hard origin/master')
        BluesteelProjectController.create_command(command_set_fetch, 2, 'git clean -f -d -q')
        BluesteelProjectController.create_command(command_set_fetch, 3, 'git fetch --all')
        BluesteelProjectController.create_command(command_set_fetch, 4, 'git pull -r origin master')
        BluesteelProjectController.create_command(command_set_fetch, 5, 'git checkout master')
        BluesteelProjectController.create_command(command_set_fetch, 6, 'git submodule sync')
        BluesteelProjectController.create_command(command_set_fetch, 7, 'git submodule update --init --recursive')
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
        BluesteelProjectController.create_default_command_set_pull(group, 2)
        return group

    @staticmethod
    def delete_project(project):
        CommandGroupEntry.objects.delete_command_group_by_id(project.command_group.id)
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
    def get_project_git_branch_data(project):
        """ Returns branch data associated with a project """
        return GitController.get_all_branches_trimmed_by_merge_target(project)


    @staticmethod
    def get_project_single_git_branch_data(project, branch):
        """ Returns a single branch data associated with a project """
        return GitController.get_single_branch_trimmed_by_merge_target(project, branch)

