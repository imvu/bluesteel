""" Bluesteel CommandSet tests """

from django.test import TestCase
from app.service.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.service.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.service.bluesteel.models.BluesteelCommandSetModel import BluesteelCommandSetEntry
from app.service.bluesteel.models.BluesteelCommandModel import BluesteelCommandEntry
from app.service.gitrepo.models.GitProjectModel import GitProjectEntry

class BluesteelCommandSetTestCase(TestCase):

    def setUp(self):
        self.layout = BluesteelLayoutEntry.objects.create(
            name='layout-1'
        )

        self.git_project = GitProjectEntry.objects.create(
            url='http://www.test.com',
            name='git-project-28',
        )

        self.project = BluesteelProjectEntry.objects.create(
            layout=self.layout,
            archive='archive-28',
            name='project-1',
            git_project=self.git_project,
        )


    def tearDown(self):
        pass

    def create_command(self, set, order, command):
        comm = BluesteelCommandEntry.objects.create(
            bluesteel_command_set=set,
            order=order,
            command=command,
        )

        return comm


    def test_get_command_set_as_object(self):
        command_set = BluesteelCommandSetEntry.objects.create(
            bluesteel_project=self.project,
            command_set_type=BluesteelCommandSetEntry.FETCH,
        )

        comm_2 = self.create_command(command_set, 2, 'com2 arg2 arg3')
        comm_3 = self.create_command(command_set, 3, 'com3 arg2 arg3')
        comm_1 = self.create_command(command_set, 1, 'com1 arg2 arg3')

        obj = command_set.as_object()

        self.assertEqual('FETCH', obj['type'])
        self.assertEqual(3, len(obj['commands']))
        self.assertEqual(1, obj['commands'][0]['order'])
        self.assertEqual(2, obj['commands'][1]['order'])
        self.assertEqual(3, obj['commands'][2]['order'])
        self.assertEqual('com1 arg2 arg3', obj['commands'][0]['command'])
        self.assertEqual('com2 arg2 arg3', obj['commands'][1]['command'])
        self.assertEqual('com3 arg2 arg3', obj['commands'][2]['command'])
