""" Presenter Views tests """

from django.test import TestCase
from django.test import Client
from django.utils import timezone
from app.logic.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.logic.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.logic.gitrepo.models.GitProjectModel import GitProjectEntry
from app.logic.gitrepo.models.GitBranchModel import GitBranchEntry
from app.logic.gitrepo.models.GitCommitModel import GitCommitEntry
from app.logic.gitrepo.models.GitUserModel import GitUserEntry
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

        self.assertEqual(4, CommandEntry.objects.all().count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-28').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-29').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-30').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-31').count())


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


    def test_get_project_list_from_layout(self):
        command_group = CommandGroupEntry.objects.create()

        git_project1 = GitProjectEntry.objects.create(url='', name='git-project-1')
        git_project2 = GitProjectEntry.objects.create(url='', name='git-project-2')
        git_project3 = GitProjectEntry.objects.create(url='', name='git-project-3')

        bluesteel_proj1 = BluesteelProjectEntry.objects.create(name='project-1', layout=self.layout_1, command_group=command_group, git_project=git_project1)
        bluesteel_proj2 = BluesteelProjectEntry.objects.create(name='project-2', layout=self.layout_1, command_group=command_group, git_project=git_project2)
        bluesteel_proj3 = BluesteelProjectEntry.objects.create(name='project-3', layout=self.layout_1, command_group=command_group, git_project=git_project3)

        resp = self.client.get('/main/layout/{0}/projects/list/'.format(self.layout_1.id))

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual(3, len(resp_obj['data']['projects']))
        self.assertEqual(bluesteel_proj1.id, resp_obj['data']['projects'][0]['id'])
        self.assertEqual(bluesteel_proj2.id, resp_obj['data']['projects'][1]['id'])
        self.assertEqual(bluesteel_proj3.id, resp_obj['data']['projects'][2]['id'])
        self.assertEqual('project-1', resp_obj['data']['projects'][0]['name'])
        self.assertEqual('project-2', resp_obj['data']['projects'][1]['name'])
        self.assertEqual('project-3', resp_obj['data']['projects'][2]['name'])
        self.assertEqual('/main/project/1/branch/list/', resp_obj['data']['projects'][0]['url']['project_branch_list'])
        self.assertEqual('/main/project/2/branch/list/', resp_obj['data']['projects'][1]['url']['project_branch_list'])
        self.assertEqual('/main/project/3/branch/list/', resp_obj['data']['projects'][2]['url']['project_branch_list'])

    def test_get_project_branch_names_list(self):
        command_group = CommandGroupEntry.objects.create()

        git_project1 = GitProjectEntry.objects.create(url='', name='git-project-1')
        git_user1 = GitUserEntry.objects.create(project=git_project1)
        git_commit1 = GitCommitEntry.objects.create(
            project=git_project1,
            commit_hash='0000100001000010000100001000010000100001',
            author=git_user1,
            author_date=timezone.now(),
            committer=git_user1,
            committer_date=timezone.now()
        )

        git_branch1 = GitBranchEntry.objects.create(project=git_project1, name='branch-1', commit=git_commit1, order=0)
        git_branch2 = GitBranchEntry.objects.create(project=git_project1, name='branch-2', commit=git_commit1, order=1)
        git_branch3 = GitBranchEntry.objects.create(project=git_project1, name='branch-3', commit=git_commit1, order=2)

        bluesteel_proj1 = BluesteelProjectEntry.objects.create(name='project-1', layout=self.layout_1, command_group=command_group, git_project=git_project1)

        resp = self.client.get('/main/project/{0}/branch/list/'.format(bluesteel_proj1.id))

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual(3, len(resp_obj['data']['branches']))
        self.assertEqual(git_branch1.id, resp_obj['data']['branches'][0]['id'])
        self.assertEqual(git_branch2.id, resp_obj['data']['branches'][1]['id'])
        self.assertEqual(git_branch3.id, resp_obj['data']['branches'][2]['id'])
        self.assertEqual('branch-1', resp_obj['data']['branches'][0]['name'])
        self.assertEqual('branch-2', resp_obj['data']['branches'][1]['name'])
        self.assertEqual('branch-3', resp_obj['data']['branches'][2]['name'])

