""" Test Command Helper file """

from app.util.commandrepo.models.CommandGroupModel import CommandGroupEntry
from app.util.commandrepo.models.CommandSetModel import CommandSetEntry
from app.util.commandrepo.models.CommandModel import CommandEntry
from app.util.commandrepo.models.CommandResultModel import CommandResultEntry

def create_default_group():
    """ Creates a default command group on the DB """
    group_entry = CommandGroupEntry.objects.create()
    return group_entry

def create_default_set():
    """ Creates a default command set and group on the DB """
    group_entry = create_default_group()
    set_entry = CommandSetEntry.objects.create(
        group=group_entry
    )
    return set_entry

def create_default_command():
    """ Creates a default command on the DB """
    set_entry = create_default_set()
    command_entry = CommandEntry.objects.create(
        command_set=set_entry,
        command='command1'
    )

    return command_entry

def create_default_command_result():
    """ Creates a default command result on the DB """
    command_entry = create_default_command()
    command_result_entry = CommandResultEntry.objects.create(
        command=command_entry,
        out='default-out',
        error='default-error',
        status=0
    )

    return command_result_entry


def create_command_at_set(command_set, command):
    """ create a command on set """
    command_entry = CommandEntry.objects.create(
        command_set=command_set,
        command=command
    )

    return command_entry

def create_command_result_at_command(command, out, error, status):
    """ Creates a default command result on the DB """
    command_result_entry = CommandResultEntry.objects.create(
        command=command,
        out=out,
        error=error,
        status=status
    )

    return command_result_entry
