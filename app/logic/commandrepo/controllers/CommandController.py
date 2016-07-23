""" Controller for Command entries """

from app.logic.commandrepo.models.CommandGroupModel import CommandGroupEntry
from app.logic.commandrepo.models.CommandModel import CommandEntry
from app.logic.commandrepo.models.CommandResultModel import CommandResultEntry
from app.logic.commandrepo.models.CommandSetModel import CommandSetEntry

class CommandController(object):
    """ Command Controller """

    @staticmethod
    def delete_command_group_by_id(command_group_id):
        """ Delete a whole command group and its associated objects """
        command_group_entry = CommandGroupEntry.objects.filter(id=command_group_id).first()

        if command_group_entry is None:
            return

        command_sets = CommandSetEntry.objects.filter(group=command_group_entry)

        for com_set in command_sets:
            CommandController.delete_command_set_by_id(com_set.id)

        command_group_entry.delete()

    @staticmethod
    def delete_command_set_by_id(command_set_id):
        """ Delete a whole command set and its associated objects """
        command_set_entry = CommandSetEntry.objects.filter(id=command_set_id).first()

        if command_set_entry is None:
            return

        commands = CommandEntry.objects.filter(command_set=command_set_entry)

        for command in commands:
            CommandController.delete_command_by_id(command.id)

        command_set_entry.delete()

    @staticmethod
    def delete_command_by_id(command_id):
        """ Delete a whole command and its associated objects """
        command_entry = CommandEntry.objects.filter(id=command_id).first()

        if command_entry is None:
            return

        command_result = CommandResultEntry.objects.filter(command=command_entry).first()

        if command_result is not None:
            command_result.delete()

        command_entry.delete()

    @staticmethod
    def delete_commands_of_command_set(command_set_entry):
        """ Delete all the commands on a command set """
        CommandEntry.objects.filter(command_set=command_set_entry).delete()

    @staticmethod
    def delete_commands_sets_of_command_group(command_group_entry):
        """ Delete all commands sets on a command group """
        CommandSetEntry.objects.filter(group=command_group_entry).delete()

    @staticmethod
    def add_full_command_set(command_group, name, order, list_commands):
        """ Adds a new set of commands from a name, order and list of strings """
        set_entry = CommandSetEntry.objects.create(group=command_group, name=name, order=order)

        for index, command in enumerate(list_commands):
            CommandEntry.objects.create(
                command_set=set_entry,
                command=command,
                order=index)

        return set_entry

    @staticmethod
    def add_commands_to_command_set(command_set_entry, list_commands):
        """ Adds commands to an existing command set entry """

        for index, command in enumerate(list_commands):
            CommandEntry.objects.create(
                command_set=command_set_entry,
                command=command,
                order=index)
