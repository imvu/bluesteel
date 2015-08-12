""" Manager for CommandGroup entries """

from django.db import models
from app.util.commandrepo.models.CommandModel import CommandEntry
from app.util.commandrepo.models.CommandResultModel import CommandResultEntry
from app.util.commandrepo.models.CommandSetModel import CommandSetEntry

# pylint: disable=R0904

# Class has not __init__ method
# pylint: disable=W0232

class CommandGroupManager(models.Manager):
    """ Command Manager """

    def delete_command_group_by_id(self, command_group_id):
        """ Delete a whole command group and its associated objects """
        command_group_entry = self.filter(id=command_group_id).first()

        if command_group_id == None:
            return

        command_sets = CommandSetEntry.objects.filter(group=command_group_entry)

        for com_set in command_sets:
            command_entries = CommandEntry.objects.filter(command_set=com_set)

            for com_ent in command_entries:
                command_result = CommandResultEntry.objects.filter(command=com_ent)
                command_result.delete()
                com_ent.delete()

            com_set.delete()

        command_group_entry.delete()

    @staticmethod
    def add_full_command_set(command_group, name, order, list_commands):
        """ Adds a new set of commands from a name, order and list of strings """
        set_entry = CommandSetEntry.objects.create(group=command_group, name=name, order=order)

        for index, command in enumerate(list_commands):
            CommandEntry.objects.create(
                command_set=set_entry,
                command=command,
                order=index)
