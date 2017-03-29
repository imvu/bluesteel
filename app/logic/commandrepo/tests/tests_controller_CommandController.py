""" CommandGroup Manager tests """

from django.test import TestCase
from app.logic.commandrepo.controllers.CommandController import CommandController
from app.logic.commandrepo.models.CommandModel import CommandEntry
from app.logic.commandrepo.models.CommandResultModel import CommandResultEntry
from app.logic.commandrepo.models.CommandSetModel import CommandSetEntry
from app.logic.commandrepo.models.CommandGroupModel import CommandGroupEntry
from app.logic.commandrepo.helper import TestCommandHelper

class CommandControllerTestCase(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_delete_command_group(self):
        result = TestCommandHelper.create_default_command_result()

        self.assertEqual(1, CommandGroupEntry.objects.all().count())
        self.assertEqual(1, CommandSetEntry.objects.all().count())
        self.assertEqual(1, CommandEntry.objects.all().count())
        self.assertEqual(1, CommandResultEntry.objects.all().count())

        CommandController.delete_command_group_by_id(CommandGroupEntry.objects.all().first().id)

        self.assertEqual(0, CommandGroupEntry.objects.all().count())
        self.assertEqual(0, CommandSetEntry.objects.all().count())
        self.assertEqual(0, CommandEntry.objects.all().count())
        self.assertEqual(0, CommandResultEntry.objects.all().count())

    def test_add_full_command_set(self):
        command_group = CommandGroupEntry.objects.create()

        self.assertEqual(1, CommandGroupEntry.objects.all().count())
        self.assertEqual(0, CommandSetEntry.objects.all().count())
        self.assertEqual(0, CommandEntry.objects.all().count())
        self.assertEqual(0, CommandResultEntry.objects.all().count())

        commands = []
        commands.append(['command 1'])
        commands.append(['command 2'])
        commands.append(['command 3'])

        CommandController.add_full_command_set(command_group, 'CLONE', 28, commands)

        self.assertEqual(1, CommandGroupEntry.objects.all().count())
        self.assertEqual(1, CommandSetEntry.objects.all().count())
        self.assertEqual(3, CommandEntry.objects.all().count())
        self.assertEqual(0, CommandResultEntry.objects.all().count())

    def test_add_full_command_set_with_group_to_none(self):
        self.assertEqual(0, CommandGroupEntry.objects.all().count())
        self.assertEqual(0, CommandSetEntry.objects.all().count())
        self.assertEqual(0, CommandEntry.objects.all().count())
        self.assertEqual(0, CommandResultEntry.objects.all().count())

        commands = []
        commands.append(['command 1'])
        commands.append(['command 2'])
        commands.append(['command 3'])

        CommandController.add_full_command_set(None, 'CLONE', 28, commands)

        self.assertEqual(0, CommandGroupEntry.objects.all().count())
        self.assertEqual(1, CommandSetEntry.objects.all().count())
        self.assertEqual(3, CommandEntry.objects.all().count())
        self.assertEqual(0, CommandResultEntry.objects.all().count())

    def test_delete_commands_from_command_set(self):
        group = TestCommandHelper.create_default_group()

        comm_set = CommandSetEntry.objects.create(
            group=group,
            name='name_set',
            order=0
        )

        CommandEntry.objects.create(
            command_set=comm_set,
            command='command1',
            order=0
        )

        CommandEntry.objects.create(
            command_set=comm_set,
            command='command2',
            order=1
        )

        CommandEntry.objects.create(
            command_set=comm_set,
            command='command3',
            order=2
        )

        self.assertEqual(1, CommandGroupEntry.objects.all().count())
        self.assertEqual(1, CommandSetEntry.objects.all().count())
        self.assertEqual(3, CommandEntry.objects.all().count())
        self.assertEqual(0, CommandResultEntry.objects.all().count())

        CommandController.delete_commands_of_command_set(comm_set)

        self.assertEqual(1, CommandGroupEntry.objects.all().count())
        self.assertEqual(1, CommandSetEntry.objects.all().count())
        self.assertEqual(0, CommandEntry.objects.all().count())
        self.assertEqual(0, CommandResultEntry.objects.all().count())

    def test_duplicate_command_set(self):
        comm_set = CommandSetEntry.objects.create(name='name_set', order=0)

        CommandEntry.objects.create(command_set=comm_set, command='command1', order=0)
        CommandEntry.objects.create(command_set=comm_set, command='command2', order=1)
        CommandEntry.objects.create(command_set=comm_set, command='command3', order=2)

        self.assertEqual(0, CommandGroupEntry.objects.all().count())
        self.assertEqual(1, CommandSetEntry.objects.all().count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=comm_set, command='command1').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=comm_set, command='command2').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=comm_set, command='command3').count())
        self.assertEqual(0, CommandResultEntry.objects.all().count())

        new_comm_set = CommandController.duplicate_command_set(comm_set.id)

        self.assertEqual(0, CommandGroupEntry.objects.all().count())
        self.assertEqual(2, CommandSetEntry.objects.all().count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=comm_set, command='command1').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=comm_set, command='command2').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=comm_set, command='command3').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=new_comm_set, command='command1').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=new_comm_set, command='command2').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=new_comm_set, command='command3').count())
        self.assertEqual(0, CommandResultEntry.objects.all().count())
