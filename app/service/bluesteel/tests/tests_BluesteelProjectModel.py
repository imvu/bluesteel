""" Bluesteel Project tests """

from django.test import TestCase
from app.service.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.service.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.service.bluesteel.models.BluesteelCommandSetModel import BluesteelCommandSetEntry
from app.service.gitrepo.models.GitProjectModel import GitProjectEntry

class BluesteelProjectTestCase(TestCase):

    def setUp(self):
        self.layout = BluesteelLayoutEntry.objects.create(name='layout-1')
        self.git_project = GitProjectEntry.objects.create(
            url='http://www.test.com',
            name='git-project-28',
        )


    def tearDown(self):
        pass

    def test_get_entry_as_object(self):
        project_entry = BluesteelProjectEntry.objects.create(
            layout=self.layout,
            archive='archive-28',
            name='project-28',
            git_project=self.git_project,
        )

        comm_set_1 = BluesteelCommandSetEntry.objects.create(
            bluesteel_project=project_entry,
            command_set_type=BluesteelCommandSetEntry.FETCH,
            )

        comm_set_2 = BluesteelCommandSetEntry.objects.create(
            bluesteel_project=project_entry,
            command_set_type=BluesteelCommandSetEntry.CLONE,
            )

        obj = project_entry.as_object()

        self.assertEqual('project-28', obj['name'])
        self.assertEqual('archive-28', obj['archive'])
        self.assertEqual('git-project-28', obj['git_project']['name'])
        self.assertEqual(self.git_project.id, obj['git_project']['id'])
        self.assertEqual(2, len(obj['command_sets']))
        self.assertEqual('CLONE', obj['command_sets'][0]['type'])
        self.assertEqual('FETCH', obj['command_sets'][1]['type'])