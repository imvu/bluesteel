""" Command Set tests """

from django.test import TestCase
from django.utils import timezone
from app.logic.commandrepo.models.CommandGroupModel import CommandGroupEntry
from app.logic.commandrepo.models.CommandSetModel import CommandSetEntry
from app.logic.commandrepo.models.CommandModel import CommandEntry
from app.logic.commandrepo.helper import TestCommandHelper

class CommandSetEntryTestCase(TestCase):

    def setUp(self):
        self.group = CommandGroupEntry.objects.create()
        self.command_set = CommandSetEntry.objects.create(
            group=self.group
        )

    def tearDown(self):
        pass

    def test_create_command_set_entry_and_as_obj(self):
        date_now = timezone.now()

        group_entry = TestCommandHelper.create_default_group()

        command_set = CommandSetEntry.objects.create(
            group=group_entry,
            name='set-name',
            order=28
        )

        command = TestCommandHelper.create_command_at_set(command_set, 'command-1-2')
        TestCommandHelper.create_command_result_at_command(command, 'out1', 'error2', 29)

        obj = command_set.as_object()
        self.assertEqual('set-name', obj['name'])
        self.assertEqual(28, obj['order'])
        self.assertEqual(1, len(obj['commands']))
        self.assertEqual('command-1-2', obj['commands'][0]['command'])
        self.assertEqual('out1', obj['commands'][0]['result']['out'])
        self.assertEqual('error2', obj['commands'][0]['result']['error'])
        self.assertEqual(29, obj['commands'][0]['result']['status'])

