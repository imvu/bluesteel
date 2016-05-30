""" Presenter Views tests """

from django.test import TestCase
from django.test import Client
from app.logic.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.logic.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.logic.gitrepo.models.GitProjectModel import GitProjectEntry
from app.logic.commandrepo.controllers.CommandController import CommandController
from app.logic.commandrepo.models.CommandGroupModel import CommandGroupEntry
from app.logic.commandrepo.models.CommandSetModel import CommandSetEntry
from app.logic.commandrepo.models.CommandModel import CommandEntry
from app.logic.httpcommon import res
import json

class BluesteelViewProjectTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.layout_1 = BluesteelLayoutEntry.objects.create(
            name='layout-1',
            active=True,
        )

        self.layout_2 = BluesteelLayoutEntry.objects.create(
            name='layout-2',
        )

        self.layout_3 = BluesteelLayoutEntry.objects.create(
            name='layout-3',
        )


    def tearDown(self):
        pass

    def test_save_bluesteel_project(self):
        commands = []
        commands.append('command-1')
        commands.append('command-2')
        commands.append('command-3')

        commands2 = []
        commands2.append('command-4')
        commands2.append('command-5')
        commands2.append('command-6')

        command_group = CommandGroupEntry.objects.create()
        CommandController.add_full_command_set(command_group, "CLONE", 0, commands)
        CommandController.add_full_command_set(command_group, "FETCH", 1, commands2)

        git_project = GitProjectEntry.objects.create(url='', name='git-project')

        bluesteel_proj = BluesteelProjectEntry.objects.create(
            name='project-1',
            layout=self.layout_1,
            command_group=command_group,
            git_project=git_project
        )

        self.assertEqual(1, CommandGroupEntry.objects.all().count())
        self.assertEqual(2, CommandSetEntry.objects.all().count())
        self.assertEqual(6, CommandEntry.objects.all().count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-1').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-2').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-3').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-4').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-5').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-6').count())

        obj = {}
        obj['name'] = 'NAME-updated'
        obj['git_project_folder_search_path'] = 'local/path/updated/too/'
        obj['clone'] = []
        obj['clone'].append('command-28')
        obj['clone'].append('command-29')
        obj['fetch'] = []
        obj['fetch'].append('command-30')
        obj['fetch'].append('command-31')

        resp = self.client.post(
            '/main/project/{0}/save/'.format(bluesteel_proj.id),
            data = json.dumps(obj),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual('NAME-updated', BluesteelProjectEntry.objects.all().first().name)
        self.assertEqual('local/path/updated/too/', BluesteelProjectEntry.objects.all().first().git_project_folder_search_path)
        self.assertEqual(1, CommandGroupEntry.objects.all().count())
        self.assertEqual(2, CommandSetEntry.objects.all().count())
        self.assertEqual(4, CommandEntry.objects.all().count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-28').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-29').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-30').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-31').count())

    def test_save_bluesteel_project_does_not_delete_benchmark_definitions(self):
        commands = []
        commands.append('command-1')
        commands.append('command-2')
        commands.append('command-3')

        command_group = CommandGroupEntry.objects.create()
        CommandController.add_full_command_set(command_group, "CLONE", 0, commands)

        git_project = GitProjectEntry.objects.create(url='', name='git-project')

        bluesteel_proj = BluesteelProjectEntry.objects.create(
            name='project-1',
            layout=self.layout_1,
            command_group=command_group,
            git_project=git_project
        )

        benchmark_def = BenchmarkDefinitionEntry.objects.create(
            layout=self.layout_1,
            project=bluesteel_proj,
            command_set=CommandSetEntry.objects.create()
        )

        self.assertEqual(1, CommandGroupEntry.objects.all().count())
        self.assertEqual(2, CommandSetEntry.objects.all().count())
        self.assertEqual(3, CommandEntry.objects.all().count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-1').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-2').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-3').count())

        obj = {}
        obj['name'] = 'NAME-updated'
        obj['git_project_folder_search_path'] = 'local/path/updated/too/'
        obj['clone'] = []
        obj['clone'].append('command-28')
        obj['clone'].append('command-29')
        obj['fetch'] = []
        obj['fetch'].append('command-30')
        obj['fetch'].append('command-31')

        resp = self.client.post(
            '/main/project/{0}/save/'.format(bluesteel_proj.id),
            data = json.dumps(obj),
            content_type='application/json')

        self.assertEqual(1, BenchmarkDefinitionEntry.objects.filter(id=benchmark_def.id).count())


    def test_save_bluesteel_project_removing_path_dots(self):
        commands = []
        commands.append('command-1')
        commands.append('command-2')
        commands.append('command-3')

        commands2 = []
        commands2.append('command-4')
        commands2.append('command-5')
        commands2.append('command-6')

        command_group = CommandGroupEntry.objects.create()
        CommandController.add_full_command_set(command_group, "CLONE", 0, commands)
        CommandController.add_full_command_set(command_group, "FETCH", 1, commands2)

        git_project = GitProjectEntry.objects.create(url='', name='git-project')

        bluesteel_proj = BluesteelProjectEntry.objects.create(
            name='project-1',
            layout=self.layout_1,
            command_group=command_group,
            git_project=git_project
        )

        obj = {}
        obj['name'] = 'NAME-updated'
        obj['git_project_folder_search_path'] = 'local/path/without/../dots/'
        obj['clone'] = []
        obj['clone'].append('command-28')
        obj['clone'].append('command-29')
        obj['fetch'] = []
        obj['fetch'].append('command-30')
        obj['fetch'].append('command-31')

        resp = self.client.post(
            '/main/project/{0}/save/'.format(bluesteel_proj.id),
            data = json.dumps(obj),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual('local/path/without/dots/', BluesteelProjectEntry.objects.all().first().git_project_folder_search_path)

    def test_save_bluesteel_project_removing_path_dots_forward(self):
        commands = []
        commands.append('command-1')
        commands.append('command-2')
        commands.append('command-3')

        commands2 = []
        commands2.append('command-4')
        commands2.append('command-5')
        commands2.append('command-6')

        command_group = CommandGroupEntry.objects.create()
        CommandController.add_full_command_set(command_group, "CLONE", 0, commands)
        CommandController.add_full_command_set(command_group, "FETCH", 1, commands2)

        git_project = GitProjectEntry.objects.create(url='', name='git-project')

        bluesteel_proj = BluesteelProjectEntry.objects.create(
            name='project-1',
            layout=self.layout_1,
            command_group=command_group,
            git_project=git_project
        )

        obj = {}
        obj['name'] = 'NAME-updated'
        obj['git_project_folder_search_path'] = 'local\\path\\without\\..\\dots\\'
        obj['clone'] = []
        obj['clone'].append('command-28')
        obj['clone'].append('command-29')
        obj['fetch'] = []
        obj['fetch'].append('command-30')
        obj['fetch'].append('command-31')

        resp = self.client.post(
            '/main/project/{0}/save/'.format(bluesteel_proj.id),
            data = json.dumps(obj),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual('local\\path\\without\\dots\\', BluesteelProjectEntry.objects.all().first().git_project_folder_search_path)

    def test_save_bluesteel_project_removing_everything_in_path(self):
        commands = []
        commands.append('command-1')
        commands.append('command-2')
        commands.append('command-3')

        commands2 = []
        commands2.append('command-4')
        commands2.append('command-5')
        commands2.append('command-6')

        command_group = CommandGroupEntry.objects.create()
        CommandController.add_full_command_set(command_group, "CLONE", 0, commands)
        CommandController.add_full_command_set(command_group, "FETCH", 1, commands2)

        git_project = GitProjectEntry.objects.create(url='', name='git-project')

        bluesteel_proj = BluesteelProjectEntry.objects.create(
            name='project-1',
            layout=self.layout_1,
            command_group=command_group,
            git_project=git_project
        )

        obj = {}
        obj['name'] = 'NAME-updated'
        obj['git_project_folder_search_path'] = '\\..\\'
        obj['clone'] = []
        obj['clone'].append('command-28')
        obj['clone'].append('command-29')
        obj['fetch'] = []
        obj['fetch'].append('command-30')
        obj['fetch'].append('command-31')

        resp = self.client.post(
            '/main/project/{0}/save/'.format(bluesteel_proj.id),
            data = json.dumps(obj),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual('.', BluesteelProjectEntry.objects.all().first().git_project_folder_search_path)

    def test_delete_bluesteel_project(self):
        commands = []
        commands.append('command-1')
        commands.append('command-2')
        commands.append('command-3')

        commands2 = []
        commands2.append('command-4')
        commands2.append('command-5')
        commands2.append('command-6')

        command_group = CommandGroupEntry.objects.create()
        CommandController.add_full_command_set(command_group, "CLONE", 0, commands)
        CommandController.add_full_command_set(command_group, "FETCH", 1, commands2)

        git_project = GitProjectEntry.objects.create(url='', name='git-project')

        bluesteel_proj = BluesteelProjectEntry.objects.create(
            name='project-1',
            layout=self.layout_1,
            command_group=command_group,
            git_project=git_project
        )

        self.assertEqual(1, CommandGroupEntry.objects.all().count())
        self.assertEqual(2, CommandSetEntry.objects.all().count())
        self.assertEqual(6, CommandEntry.objects.all().count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-1').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-2').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-3').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-4').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-5').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-6').count())
        self.assertEqual(1, GitProjectEntry.objects.all().count())
        self.assertEqual(True, BluesteelLayoutEntry.objects.all().first().active)

        resp = self.client.post(
            '/main/project/{0}/delete/'.format(bluesteel_proj.id),
            data = '',
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual(0, BluesteelProjectEntry.objects.all().count())
        self.assertEqual(0, CommandGroupEntry.objects.all().count())
        self.assertEqual(0, CommandSetEntry.objects.all().count())
        self.assertEqual(0, CommandEntry.objects.all().count())
        self.assertEqual(0, GitProjectEntry.objects.all().count())
        self.assertEqual(False, BluesteelLayoutEntry.objects.all().first().active)

