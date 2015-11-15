""" BenchmarkExecution Model tests """

from django.test import TestCase
from django.utils import timezone
from app.service.benchmark.models.BenchmarkExecutionModel import BenchmarkExecutionEntry
from app.service.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.service.gitrepo.models.GitProjectModel import GitProjectEntry
from app.service.gitrepo.models.GitUserModel import GitUserEntry
from app.service.gitrepo.models.GitCommitModel import GitCommitEntry
from app.service.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.service.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.util.commandrepo.models.CommandGroupModel import CommandGroupEntry
from app.util.commandrepo.models.CommandSetModel import CommandSetEntry
from datetime import timedelta

class BenchmarkExecutionEntryTestCase(TestCase):

    def setUp(self):
        self.git_project = GitProjectEntry.objects.create(url='http://test/')
        self.git_user = GitUserEntry.objects.create(
            project=self.git_project,
            name='user1',
            email='user1@test.com'
        )

        self.git_commit = GitCommitEntry.objects.create(
            project=self.git_project,
            commit_hash='0000100001000010000100001000010000100001',
            author=self.git_user,
            author_date=timezone.now(),
            committer=self.git_user,
            committer_date=timezone.now()
        )

        self.command_group = CommandGroupEntry.objects.create()
        self.command_set = CommandSetEntry.objects.create(
            group=self.command_group
        )

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

    def test_benchmark_execution_as_object(self):
        entry = BenchmarkExecutionEntry.objects.create(
            definition=self.benchmark_definition,
            commit=self.git_commit,
            report=self.command_set,
            invalidated=False,
            status=BenchmarkExecutionEntry.STATUS_TYPE[1][0]
        )

        obj = entry.as_object()

        self.assertEqual('0000100001000010000100001000010000100001', obj['commit'])
        self.assertEqual('project-1', obj['definition']['project']['uuid'])
        self.assertEqual(1, obj['definition']['project']['id'])
        self.assertEqual('http://test/', obj['definition']['project']['git_project']['url'])
        self.assertEqual(0, len(obj['definition']['project']['git_project']['branches']) )
        self.assertEqual('default-name', obj['definition']['project']['git_project']['name'])
        self.assertEqual(0, len(obj['report']['commands']))
        self.assertEqual(True, obj['invalidated'])
        self.assertEqual(1, obj['status']['index'])
        self.assertEqual('In_Progress', obj['status']['name'])


