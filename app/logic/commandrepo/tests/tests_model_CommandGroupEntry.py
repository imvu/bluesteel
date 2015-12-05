""" Command Group tests """

from django.test import TestCase
from django.utils import timezone
from app.logic.commandrepo.models.CommandGroupModel import CommandGroupEntry
from app.logic.commandrepo.models.CommandSetModel import CommandSetEntry
from app.logic.commandrepo.models.CommandModel import CommandEntry
from app.logic.commandrepo.helper import TestCommandHelper

class CommandGroupEntryTestCase(TestCase):

    def setUp(self):
        self.group = TestCommandHelper.create_default_group()

    def tearDown(self):
        pass

    def test_create_command_group_entry_and_as_obj(self):
        date_now = timezone.now()

        command_set = CommandSetEntry.objects.create(
            group=self.group,
            name='set-name',
            order=28
        )

        command = TestCommandHelper.create_command_at_set(command_set, 'command-1-2')
        TestCommandHelper.create_command_result_at_command(command, 'out1', 'error2', 29)

        obj = self.group.as_object()
        comm_set = obj['command_sets'][0]
        self.assertEqual('set-name', comm_set['name'])
        self.assertEqual(28, comm_set['order'])
        self.assertEqual(1, len(comm_set['commands']))
        self.assertEqual('command-1-2', comm_set['commands'][0]['command'])
        self.assertEqual('out1', comm_set['commands'][0]['result']['out'])
        self.assertEqual('error2', comm_set['commands'][0]['result']['error'])
        self.assertEqual(29, comm_set['commands'][0]['result']['status'])

