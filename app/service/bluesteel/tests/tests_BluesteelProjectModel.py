""" Bluesteel Project tests """

from django.test import TestCase
from app.service.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.service.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.service.gitrepo.models.GitProjectModel import GitProjectEntry
from app.util.commandrepo.models.CommandGroupModel import CommandGroupEntry
from app.util.commandrepo.models.CommandSetModel import CommandSetEntry
from app.util.commandrepo.models.CommandModel import CommandEntry

class BluesteelProjectTestCase(TestCase):

    def setUp(self):
        self.git_project = GitProjectEntry.objects.create(
            url='http://www.test.com',
            name='git-project-28',
        )

        self.command_group = CommandGroupEntry.objects.create()
        self.command_set = CommandSetEntry.objects.create(
            group=self.command_group
        )

        self.command = CommandEntry.objects.create(
            command_set=self.command_set,
            command='command-1 arg-2, arg-3',
            order=0
        )

        self.layout = BluesteelLayoutEntry.objects.create(
            name='layout-1',
            archive='archive-28',
        )

        self.project = BluesteelProjectEntry.objects.create(
            name='project-1',
            layout=self.layout,
            command_group=self.command_group,
            git_project=self.git_project,
        )


    def tearDown(self):
        pass

    def test_get_entry_as_object(self):
        obj = self.project.as_object()

        self.assertEqual('project-1', obj['name'])
        # self.assertEqual('git-project-28', obj['git_project']['name'])
        # self.assertEqual(self.git_project.id, obj['git_project']['id'])
        self.assertEqual(1, len(obj['command_group']['command_sets']))
