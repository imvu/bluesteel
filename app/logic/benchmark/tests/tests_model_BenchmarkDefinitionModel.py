""" BenchmarkDefinition Model tests """

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from app.logic.benchmark.models.BenchmarkExecutionModel import BenchmarkExecutionEntry
from app.logic.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.logic.gitrepo.models.GitProjectModel import GitProjectEntry
from app.logic.gitrepo.models.GitUserModel import GitUserEntry
from app.logic.gitrepo.models.GitCommitModel import GitCommitEntry
from app.logic.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.logic.bluesteelworker.models.WorkerModel import WorkerEntry
from app.logic.commandrepo.models.CommandGroupModel import CommandGroupEntry
from app.logic.commandrepo.models.CommandSetModel import CommandSetEntry
from app.logic.commandrepo.models.CommandModel import CommandEntry
from app.logic.commandrepo.models.CommandResultModel import CommandResultEntry
from datetime import timedelta
import datetime
import json

class BenchmarkDefinitionEntryTestCase(TestCase):

    def setUp(self):
        self.git_project = GitProjectEntry.objects.create(url='http://test/')

        self.command_group = CommandGroupEntry.objects.create()
        self.command_set = CommandSetEntry.objects.create()

        self.bluesteel_layout = BluesteelLayoutEntry.objects.create(
            name='Layout',
            active=True,
            project_index_path=0,
        )

        self.bluesteel_project = BluesteelProjectEntry.objects.create(
            name='Project',
            order=0,
            layout=self.bluesteel_layout,
            command_group=self.command_group,
            git_project=self.git_project,
        )

        self.benchmark_definition = BenchmarkDefinitionEntry.objects.create(
            name='BenchmarkDefinition',
            layout=self.bluesteel_layout,
            project=self.bluesteel_project,
            command_set=self.command_set,
        )

    def tearDown(self):
        pass

    def test_benchmark_def_as_object(self):
        self.benchmark_definition.max_benchmark_date = datetime.datetime(1982, 3, 28, 0, 0, tzinfo=datetime.timezone.utc)
        self.benchmark_definition.save()

        obj = self.benchmark_definition.as_object()

        self.assertEqual(1982, obj['max_benchmark_date']['year'])
        self.assertEqual(3, obj['max_benchmark_date']['month']['number'])
        self.assertEqual('March', obj['max_benchmark_date']['month']['name'])
        self.assertEqual(28, obj['max_benchmark_date']['day'])

    def test_benchmark_def_as_object_with_max_benchmark_date(self):
        obj = self.benchmark_definition.as_object()

        self.assertEqual(self.benchmark_definition.id, obj['id'])
        self.assertEqual('BenchmarkDefinition', obj['name'])
        self.assertEqual(self.bluesteel_layout.id, obj['layout']['id'])
        self.assertEqual('Layout', obj['layout']['name'])
        self.assertEqual('archive-1', obj['layout']['uuid'])
        self.assertEqual(self.bluesteel_project.id, obj['project']['id'])
        self.assertEqual('Project', obj['project']['name'])
        self.assertEqual('project-1', obj['project']['uuid'])
        self.assertEqual('.', obj['project']['git_project_folder_search_path'])
        self.assertEqual(False, obj['active'])
        self.assertEqual(0, obj['revision'])
        self.assertEqual(0, obj['max_fluctuation_percent'])

    def test_benchmark_def_delete_also_deletes_command_set(self):
        self.assertEqual(1, BenchmarkDefinitionEntry.objects.filter(id=self.benchmark_definition.id).count())
        self.assertEqual(1, CommandSetEntry.objects.all().count())
        self.benchmark_definition.delete()
        self.assertEqual(0, BenchmarkDefinitionEntry.objects.filter(id=self.benchmark_definition.id).count())
        self.assertEqual(0, CommandSetEntry.objects.all().count())

    def test_get_max_weeks_old_names_and_values(self):
        self.benchmark_definition.max_weeks_old_notify = 2
        self.benchmark_definition.save()

        names = self.benchmark_definition.get_max_weeks_old_names_and_values()

        self.assertEqual('Allways', names[0]['name'])
        self.assertEqual('Never', names[1]['name'])
        self.assertEqual('1 Week', names[2]['name'])
        self.assertEqual('2 Weeks', names[3]['name'])
        self.assertEqual('3 Weeks', names[4]['name'])
        self.assertEqual('1 Month', names[5]['name'])
        self.assertEqual('2 Months', names[6]['name'])
        self.assertEqual('3 Months', names[7]['name'])
        self.assertEqual('4 Months', names[8]['name'])
        self.assertEqual('5 Months', names[9]['name'])
        self.assertEqual('6 Months', names[10]['name'])
        self.assertEqual('1 Year', names[11]['name'])
        self.assertEqual('2 Years', names[12]['name'])
        self.assertEqual('3 Years', names[13]['name'])
        self.assertEqual('4 Years', names[14]['name'])
        self.assertEqual('5 Years', names[15]['name'])
        self.assertEqual('10 Years', names[16]['name'])

        self.assertFalse(names[0]['current'])
        self.assertFalse(names[1]['current'])
        self.assertFalse(names[2]['current'])
        self.assertTrue(names[3]['current'])
        self.assertFalse(names[4]['current'])
        self.assertFalse(names[5]['current'])
        self.assertFalse(names[6]['current'])
        self.assertFalse(names[7]['current'])
        self.assertFalse(names[8]['current'])
        self.assertFalse(names[9]['current'])
        self.assertFalse(names[10]['current'])
        self.assertFalse(names[11]['current'])
        self.assertFalse(names[12]['current'])
        self.assertFalse(names[13]['current'])
        self.assertFalse(names[14]['current'])
        self.assertFalse(names[15]['current'])
        self.assertFalse(names[16]['current'])

