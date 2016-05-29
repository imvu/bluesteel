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

    def test_benchmark_def_delete_also_deletes_command_set(self):
        self.assertEqual(1, BenchmarkDefinitionEntry.objects.filter(id=self.benchmark_definition.id).count())
        self.assertEqual(1, CommandSetEntry.objects.all().count())
        self.benchmark_definition.delete()
        self.assertEqual(0, BenchmarkDefinitionEntry.objects.filter(id=self.benchmark_definition.id).count())
        self.assertEqual(0, CommandSetEntry.objects.all().count())

