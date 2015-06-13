""" Bluesteel Layout tests """

from django.test import TestCase
from app.service.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.service.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.service.bluesteel.managers.BluesteelLayoutManager import BluesteelLayoutManager
from app.service.gitrepo.models.GitProjectModel import GitProjectEntry

class BluesteelLayoutTestCase(TestCase):

    def setUp(self):
        self.git_project_1 = GitProjectEntry.objects.create(
            url='http://www.test-1.com',
            name='git-project-1',
        )

        self.git_project_2 = GitProjectEntry.objects.create(
            url='http://www.test-2.com',
            name='git-project-2',
        )


    def tearDown(self):
        pass

    def test_get_layout_entry_as_object(self):
        layout = BluesteelLayoutEntry.objects.create(
            name='layout-1',
            archive='archive-name',
        )

        command_group_1 = BluesteelLayoutManager.create_default_command_group()
        command_group_2 = BluesteelLayoutManager.create_default_command_group()

        project_entry_1 = BluesteelProjectEntry.objects.create(
            layout=layout,
            name='project-1',
            command_group=command_group_1,
            git_project=self.git_project_1,
        )

        project_entry_2 = BluesteelProjectEntry.objects.create(
            layout=layout,
            name='project-2',
            command_group=command_group_2,
            git_project=self.git_project_2,
        )

        obj = layout.as_object()

        self.assertEqual('layout-1', obj['name'])
        self.assertEqual('archive-name', obj['archive'])
        self.assertEqual(2, len(obj['projects']))

        self.assertEqual('project-1', obj['projects'][0]['name'])
        # self.assertEqual(self.git_project_1.id, obj['projects'][0]['git_project']['id'])

        self.assertEqual('project-2', obj['projects'][1]['name'])
        # self.assertEqual(self.git_project_2.id, obj['projects'][1]['git_project']['id'])
