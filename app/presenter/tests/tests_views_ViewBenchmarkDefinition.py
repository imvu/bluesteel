""" Presenter Views BenchmarkDefinition tests """

from django.test import TestCase
from django.test import Client
from app.service.benchmark.controllers.BenchmarkDefinitionController import BenchmarkDefinitionController
from app.service.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.service.bluesteel.controllers.BluesteelLayoutController import BluesteelLayoutController
from app.service.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.service.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.util.commandrepo.models.CommandSetModel import CommandSetEntry
from app.util.commandrepo.models.CommandModel import CommandEntry
from app.util.httpcommon import res
import json

class BenchmarkDefinitionViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_save_benchmark_definition(self):
        layout = BluesteelLayoutController.create_new_default_layout()
        definition = BenchmarkDefinitionController.create_default_benchmark_definition()

        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-1').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-2').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-3').count())

        project = BluesteelProjectEntry.objects.filter(layout=layout).first()

        obj = {}
        obj['layout_id'] = layout.id
        obj['project_id'] = project.id
        obj['command_list'] = []
        obj['command_list'].append('command-28')
        obj['command_list'].append('command-29')
        obj['command_list'].append('command-30')
        obj['command_list'].append('command-31')

        resp = self.client.post(
            '/main/definition/{0}/save/'.format(definition.id),
            data = json.dumps(obj),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])

        definition = BenchmarkDefinitionEntry.objects.filter(id=definition.id).first()

        self.assertEqual(0, CommandEntry.objects.filter(command_set=definition.command_set, command='command-1').count())
        self.assertEqual(0, CommandEntry.objects.filter(command_set=definition.command_set, command='command-2').count())
        self.assertEqual(0, CommandEntry.objects.filter(command_set=definition.command_set, command='command-3').count())

        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-28').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-29').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-30').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-31').count())
