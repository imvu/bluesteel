""" Presenter Views tests """

from django.test import TestCase
from django.test import Client
from app.service.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.service.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.service.gitrepo.models.GitProjectModel import GitProjectEntry
from app.util.commandrepo.models.CommandGroupModel import CommandGroupEntry
from app.util.commandrepo.models.CommandSetModel import CommandSetEntry
from app.util.commandrepo.models.CommandModel import CommandEntry
from app.util.httpcommon import res
import json

class BluesteelViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.layout_1 = BluesteelLayoutEntry.objects.create(
            name='layout-1',
            archive='archive-28',
        )

        self.layout_2 = BluesteelLayoutEntry.objects.create(
            name='layout-2',
            archive='archive-28',
        )

        self.layout_3 = BluesteelLayoutEntry.objects.create(
            name='layout-3',
            archive='archive-28',
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
        CommandGroupEntry.objects.add_full_command_set(command_group, "CLONE", 0, commands)
        CommandGroupEntry.objects.add_full_command_set(command_group, "FETCH", 1, commands2)

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
        obj['clone'] = []
        obj['clone'].append('command-28')
        obj['clone'].append('command-29')
        obj['fetch'] = []
        obj['fetch'].append('command-30')
        obj['fetch'].append('command-31')
        obj['pull'] = []
        obj['pull'].append('command-32')

        resp = self.client.post(
            '/main/project/{0}/save/'.format(bluesteel_proj.id),
            data = json.dumps(obj),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual(1, CommandGroupEntry.objects.all().count())
        self.assertEqual(3, CommandSetEntry.objects.all().count())
        self.assertEqual(5, CommandEntry.objects.all().count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-28').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-29').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-30').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-31').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-32').count())

