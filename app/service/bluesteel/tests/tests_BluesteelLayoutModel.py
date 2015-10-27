""" Bluesteel Layout tests """

from django.test import TestCase
from app.service.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.service.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.service.bluesteel.controllers.BluesteelProjectController import BluesteelProjectController
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

        self.layout = BluesteelLayoutEntry.objects.create(
            name='layout-1',
        )

        self.command_group_1 = BluesteelProjectController.create_default_command_group()
        self.command_group_2 = BluesteelProjectController.create_default_command_group()

        self.project_entry_1 = BluesteelProjectEntry.objects.create(
            layout=self.layout,
            name='project-1',
            command_group=self.command_group_1,
            git_project=self.git_project_1,
        )

        self.project_entry_2 = BluesteelProjectEntry.objects.create(
            layout=self.layout,
            name='project-2',
            command_group=self.command_group_2,
            git_project=self.git_project_2,
        )


    def tearDown(self):
        pass

    def test_get_layout_entry_as_object(self):
        obj = self.layout.as_object()

        self.assertEqual('layout-1', obj['name'])
        self.assertEqual('archive-{0}'.format(self.layout.id), obj['uuid'])
        self.assertEqual(2, len(obj['projects']))

        self.assertEqual('project-1', obj['projects'][0]['name'])
        # self.assertEqual(self.git_project_1.id, obj['projects'][0]['git_project']['id'])

        self.assertEqual('project-2', obj['projects'][1]['name'])
        # self.assertEqual(self.git_project_2.id, obj['projects'][1]['git_project']['id'])

    def test_clamp_project_index_path_succesful(self):
        self.layout.project_index_path = 28
        self.layout.save()

        self.assertEqual(28, self.layout.project_index_path)

        self.layout.clamp_project_index_path()

        self.assertEqual(1, self.layout.project_index_path)

    def test_clamp_project_index_path_already_clamped(self):
        self.layout.project_index_path = 0
        self.layout.save()

        self.assertEqual(0, self.layout.project_index_path)

        self.layout.clamp_project_index_path()

        self.assertEqual(0, self.layout.project_index_path)

    def test_check_active_state_and_keep_it_active(self):
        self.layout.project_index_path = 0
        self.layout.active = True
        self.layout.save()

        self.assertEqual(True, self.layout.active)

        self.layout.check_active_state()

        self.assertEqual(True, self.layout.active)

    def test_check_active_state_and_change_it_to_inactive(self):
        self.layout.project_index_path = 28
        self.layout.active = True
        self.layout.save()

        self.assertEqual(True, self.layout.active)

        self.layout.check_active_state()

        self.assertEqual(False, self.layout.active)
