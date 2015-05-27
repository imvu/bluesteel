""" Bluesteel Command tests """

from django.test import TestCase
from app.service.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.service.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.service.bluesteel.models.BluesteelCommandSetModel import BluesteelCommandSetEntry
from app.service.bluesteel.models.BluesteelCommandModel import BluesteelCommandEntry
from app.service.gitrepo.models.GitProjectModel import GitProjectEntry

class BluesteelCommandTestCase(TestCase):

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

        self.command_set = BluesteelCommandSetEntry.objects.create(
            bluesteel_project=self.project,
        )


    def tearDown(self):
        pass

    def test_get_entry_as_object(self):
        command_entry = BluesteelCommandEntry.objects.create(
            bluesteel_command_set=self.command_set,
            order=28,
            command='command1 arg2 arg3',
        )

        obj = command_entry.as_object()

        self.assertEqual('command1 arg2 arg3', obj['command'])
        self.assertEqual(28, obj['order'])
