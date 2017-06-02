""" BenchmarkDefinition Controller tests """

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from app.logic.benchmark.controllers.BenchmarkDefinitionController import BenchmarkDefinitionController
from app.logic.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.logic.benchmark.models.BenchmarkDefinitionWorkerPassModel import BenchmarkDefinitionWorkerPassEntry
from app.logic.benchmark.models.BenchmarkExecutionModel import BenchmarkExecutionEntry
from app.logic.benchmark.models.BenchmarkFluctuationOverrideModel import BenchmarkFluctuationOverrideEntry
from app.logic.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.logic.bluesteel.controllers.BluesteelProjectController import BluesteelProjectController
from app.logic.bluesteelworker.models.WorkerModel import WorkerEntry
from app.logic.gitrepo.models.GitProjectModel import GitProjectEntry
from app.logic.gitrepo.models.GitUserModel import GitUserEntry
from app.logic.gitrepo.models.GitCommitModel import GitCommitEntry
from app.logic.commandrepo.models.CommandModel import CommandEntry
from app.logic.commandrepo.models.CommandResultModel import CommandResultEntry
from app.logic.commandrepo.models.CommandSetModel import CommandSetEntry
from app.logic.commandrepo.models.CommandGroupModel import CommandGroupEntry
from app.logic.bluesteelworker.models.WorkerModel import WorkerEntry
from app.logic.commandrepo.helper import TestCommandHelper

class BenchmarkDefinitionControllerTestCase(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def get_default_commands(self):
        commands = []
        commands.append('git checkout {commit_hash}')
        commands.append('git submodule update --init --recursive')
        commands.append('<add_more_commands_here>')
        return commands

    def test_create_default_definition_commands(self):
        self.assertEqual(0, CommandGroupEntry.objects.all().count())
        self.assertEqual(0, CommandSetEntry.objects.all().count())
        self.assertEqual(0, CommandEntry.objects.all().count())
        self.assertEqual(0, CommandResultEntry.objects.all().count())

        BenchmarkDefinitionController.create_default_definition_commands()

        self.assertEqual(0, CommandGroupEntry.objects.all().count())
        self.assertEqual(1, CommandSetEntry.objects.all().count())
        self.assertEqual(3, CommandEntry.objects.all().count())
        self.assertEqual(0, CommandResultEntry.objects.all().count())

    def test_create_default_benchmark_definition_without_layout_returns_nothing(self):
        self.assertEqual(0, BluesteelLayoutEntry.objects.all().count())
        self.assertEqual(0, BluesteelProjectEntry.objects.all().count())
        self.assertEqual(None, BenchmarkDefinitionController.create_default_benchmark_definition())

    def test_create_default_benchmark_definition_without_projects_returns_nothing(self):
        new_layout = BluesteelLayoutEntry.objects.create(name='default-name')

        self.assertEqual(1, BluesteelLayoutEntry.objects.all().count())
        self.assertEqual(0, BluesteelProjectEntry.objects.all().count())
        self.assertEqual(None, BenchmarkDefinitionController.create_default_benchmark_definition())


    def test_create_default_benchmark_definition_without_projects_returns_nothing(self):
        self.assertEqual(0, CommandGroupEntry.objects.all().count())
        self.assertEqual(0, CommandSetEntry.objects.all().count())
        self.assertEqual(0, CommandEntry.objects.all().count())
        self.assertEqual(0, CommandResultEntry.objects.all().count())

        new_layout = BluesteelLayoutEntry.objects.create(name='default-name')
        project = BluesteelProjectController.create_default_project(new_layout, 'project', 0)
        definition = BenchmarkDefinitionController.create_default_benchmark_definition()

        self.assertEqual(1, BluesteelLayoutEntry.objects.all().count())
        self.assertEqual(1, BluesteelProjectEntry.objects.all().count())
        self.assertNotEqual(None, definition.command_set)
        self.assertEqual(3, CommandEntry.objects.filter(command_set=definition.command_set).count())
        self.assertEqual(0, CommandResultEntry.objects.all().count())


    def test_duplicate_benchmark_definition(self):
        self.assertEqual(0, CommandGroupEntry.objects.all().count())
        self.assertEqual(0, CommandSetEntry.objects.all().count())
        self.assertEqual(0, CommandEntry.objects.all().count())
        self.assertEqual(0, CommandResultEntry.objects.all().count())

        new_layout = BluesteelLayoutEntry.objects.create(name='default-name')
        project = BluesteelProjectController.create_default_project(new_layout, 'project', 0)
        definition = BenchmarkDefinitionController.create_default_benchmark_definition()
        definition.active = True
        definition.max_fluctuation_percent = 28
        definition.revision = 3
        definition.max_weeks_old_notify = 2
        definition.save()

        BenchmarkFluctuationOverrideEntry.objects.create(definition=definition, result_id='id1', override_value=28)
        BenchmarkFluctuationOverrideEntry.objects.create(definition=definition, result_id='id2', override_value=29)
        BenchmarkFluctuationOverrideEntry.objects.create(definition=definition, result_id='id3', override_value=30)

        self.assertEqual(1, BluesteelLayoutEntry.objects.all().count())
        self.assertEqual(1, BluesteelProjectEntry.objects.all().count())
        self.assertNotEqual(None, definition.command_set)
        self.assertEqual(3, CommandEntry.objects.filter(command_set=definition.command_set).count())
        self.assertEqual(0, CommandResultEntry.objects.all().count())
        self.assertEqual(True, definition.active)
        self.assertEqual(3, definition.revision)
        self.assertEqual(28, definition.max_fluctuation_percent)
        self.assertEqual(2, definition.max_weeks_old_notify)
        self.assertEqual('default-name', definition.name)
        self.assertEqual(3, BenchmarkFluctuationOverrideEntry.objects.all().count())

        new_definition = BenchmarkDefinitionController.duplicate_benchmark_definition(definition.id)

        self.assertNotEqual(None, new_definition)
        self.assertEqual(2, BenchmarkDefinitionEntry.objects.all().count())
        self.assertEqual(3, CommandEntry.objects.filter(command_set=definition.command_set).count())
        self.assertEqual(3, CommandEntry.objects.filter(command_set=new_definition.command_set).count())
        self.assertEqual(True, definition.active)
        self.assertEqual(False, new_definition.active)
        self.assertEqual(3, definition.revision)
        self.assertEqual(0, new_definition.revision)
        self.assertEqual(28, definition.max_fluctuation_percent)
        self.assertEqual(28, new_definition.max_fluctuation_percent)
        self.assertEqual(2, definition.max_weeks_old_notify)
        self.assertEqual(2, new_definition.max_weeks_old_notify)
        self.assertEqual('default-name', definition.name)
        self.assertEqual('default-name (duplicate)', new_definition.name)
        self.assertEqual(3, BenchmarkFluctuationOverrideEntry.objects.all().count())

    def test_save_benchmark_definition(self):
        self.assertEqual(0, CommandGroupEntry.objects.all().count())
        self.assertEqual(0, CommandSetEntry.objects.all().count())
        self.assertEqual(0, CommandEntry.objects.all().count())
        self.assertEqual(0, CommandResultEntry.objects.all().count())

        new_layout = BluesteelLayoutEntry.objects.create(name='default-name')
        project = BluesteelProjectController.create_default_project(new_layout, 'project', 0)
        definition = BenchmarkDefinitionController.create_default_benchmark_definition()

        self.assertEqual(1, BluesteelLayoutEntry.objects.all().count())
        self.assertEqual(1, BluesteelProjectEntry.objects.all().count())
        self.assertNotEqual(None, definition.command_set)
        self.assertEqual(3, CommandEntry.objects.filter(command_set=definition.command_set).count())
        self.assertEqual(0, CommandResultEntry.objects.all().count())
        self.assertEqual(False, definition.active)
        self.assertEqual(0, definition.revision)
        self.assertEqual(0, definition.max_fluctuation_percent)
        self.assertEqual(1, definition.max_weeks_old_notify)
        self.assertEqual('default-name', definition.name)
        self.assertEqual(0, BenchmarkFluctuationOverrideEntry.objects.all().count())

        commands = []
        commands.append('command-28')
        commands.append('command-29')
        commands.append('command-30')

        overrides = []
        overrides.append({'result_id' : 'id1', 'override_value' : 28})
        overrides.append({'result_id' : 'id2', 'override_value' : 29})

        definition = BenchmarkDefinitionController.save_benchmark_definition('new-name', definition.id, new_layout.id, project.id, True, commands, 28, overrides, 8, [])

        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-28').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-29').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='command-30').count())
        self.assertEqual(True, definition.active)
        self.assertEqual(1, definition.revision)
        self.assertEqual(28, definition.max_fluctuation_percent)
        self.assertEqual(8, definition.max_weeks_old_notify)
        self.assertEqual('new-name', definition.name)
        self.assertEqual(2, BenchmarkFluctuationOverrideEntry.objects.all().count())

    def test_save_same_benchmark_definition_does_not_increment_revision(self):
        self.assertEqual(0, CommandGroupEntry.objects.all().count())
        self.assertEqual(0, CommandSetEntry.objects.all().count())
        self.assertEqual(0, CommandEntry.objects.all().count())
        self.assertEqual(0, CommandResultEntry.objects.all().count())

        new_layout = BluesteelLayoutEntry.objects.create(name='default-name')
        project = BluesteelProjectController.create_default_project(new_layout, 'project', 0)
        definition = BenchmarkDefinitionController.create_default_benchmark_definition()

        self.assertEqual(1, BluesteelLayoutEntry.objects.all().count())
        self.assertEqual(1, BluesteelProjectEntry.objects.all().count())
        self.assertNotEqual(None, definition.command_set)
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='git checkout {commit_hash}').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='git submodule update --init --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='<add_more_commands_here>').count())
        self.assertEqual(0, CommandResultEntry.objects.all().count())
        self.assertEqual(False, definition.active)
        self.assertEqual(0, definition.revision)
        self.assertEqual(0, definition.max_fluctuation_percent)
        self.assertEqual(1, definition.max_weeks_old_notify)
        self.assertEqual('default-name', definition.name)
        self.assertEqual(0, BenchmarkFluctuationOverrideEntry.objects.all().count())

        commands = self.get_default_commands()

        overrides = []
        overrides.append({'result_id' : 'id1', 'override_value' : 28})
        overrides.append({'result_id' : 'id2', 'override_value' : 29})

        result = BenchmarkDefinitionController.save_benchmark_definition('default-name', definition.id, new_layout.id, project.id, True, commands, 0, overrides, 8, [])
        definition = BenchmarkDefinitionEntry.objects.all().first()

        self.assertEqual(definition, result)
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='git checkout {commit_hash}').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='git submodule update --init --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=definition.command_set, command='<add_more_commands_here>').count())
        self.assertEqual(True, definition.active)
        self.assertEqual(0, definition.revision)
        self.assertEqual(0, definition.max_fluctuation_percent)
        self.assertEqual(8, definition.max_weeks_old_notify)
        self.assertEqual('default-name', definition.name)
        self.assertEqual(2, BenchmarkFluctuationOverrideEntry.objects.all().count())

    def test_save_benchmark_definition_does_not_delete_benchmarks_executions(self):
        user1 = User.objects.create_user('user1@test.com', 'user1@test.com', 'pass')
        user1.save()

        git_project1 = GitProjectEntry.objects.create(url='http://test/')

        git_user1 = GitUserEntry.objects.create(project=git_project1, name='user1', email='user1@test.com')

        commit1 = GitCommitEntry.objects.create(project=git_project1, commit_hash='0000100001000010000100001000010000100001', author=git_user1, author_date=timezone.now(), committer=git_user1, committer_date=timezone.now())

        command_group = CommandGroupEntry.objects.create()
        command_set = CommandSetEntry.objects.create(group=command_group)

        bluesteel_layout = BluesteelLayoutEntry.objects.create(name='Layout', active=True, project_index_path=0)
        bluesteel_project = BluesteelProjectEntry.objects.create(name='Project', order=0, layout=bluesteel_layout, command_group=command_group, git_project=git_project1)

        benchmark_definition1 = BenchmarkDefinitionEntry.objects.create(name='BenchmarkDefinition1', layout=bluesteel_layout, project=bluesteel_project, command_set=command_set, revision=28)

        worker1 = WorkerEntry.objects.create(name='worker-name-1', uuid='uuid-worker-1', operative_system='osx', description='long-description-1', user=user1, git_feeder=False)
        report1 = CommandSetEntry.objects.create(group=None)

        benchmark_execution1 = BenchmarkExecutionEntry.objects.create(definition=benchmark_definition1, commit=commit1, worker=worker1, report=report1, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)

        commands = []
        commands.append('command-new-1')
        commands.append('command-new-2')
        commands.append('command-new-3')
        commands.append('command-new-4')
        commands.append('command-new-5')

        overrides = []
        overrides.append({'result_id' : 'id1', 'override_value' : 28})
        overrides.append({'result_id' : 'id2', 'override_value' : 29})

        self.assertEqual('BenchmarkDefinition1', benchmark_definition1.name)
        self.assertEqual(1, BenchmarkExecutionEntry.objects.all().count())
        self.assertEqual(benchmark_execution1, BenchmarkExecutionEntry.objects.all().first())
        self.assertEqual(0, CommandEntry.objects.filter(command_set=benchmark_definition1.command_set).count())
        self.assertEqual(0, BenchmarkFluctuationOverrideEntry.objects.all().count())

        result = BenchmarkDefinitionController.save_benchmark_definition('BenchmarkDefinition1-1', benchmark_definition1.id, bluesteel_layout.id, bluesteel_project.id, True, commands, 28, overrides, 0, [])

        self.assertEqual('BenchmarkDefinition1-1', result.name)
        self.assertEqual(1, BenchmarkExecutionEntry.objects.all().count())
        self.assertEqual(benchmark_execution1, BenchmarkExecutionEntry.objects.all().first())
        self.assertEqual(5, CommandEntry.objects.filter(command_set=benchmark_definition1.command_set).count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=benchmark_definition1.command_set, command='command-new-1').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=benchmark_definition1.command_set, command='command-new-2').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=benchmark_definition1.command_set, command='command-new-3').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=benchmark_definition1.command_set, command='command-new-4').count())
        self.assertEqual(1, CommandEntry.objects.filter(command_set=benchmark_definition1.command_set, command='command-new-5').count())
        self.assertEqual(2, BenchmarkFluctuationOverrideEntry.objects.all().count())

    def test_save_benchmark_definition_delete_benchmarks_executions_if_layout_or_project_different(self):
        user1 = User.objects.create_user('user1@test.com', 'user1@test.com', 'pass')
        user1.save()

        git_project1 = GitProjectEntry.objects.create(url='http://test/')

        git_user1 = GitUserEntry.objects.create(project=git_project1, name='user1', email='user1@test.com')

        commit1 = GitCommitEntry.objects.create(project=git_project1, commit_hash='0000100001000010000100001000010000100001', author=git_user1, author_date=timezone.now(), committer=git_user1, committer_date=timezone.now())

        command_group = CommandGroupEntry.objects.create()
        command_set = CommandSetEntry.objects.create(group=command_group)

        bluesteel_layout1 = BluesteelLayoutEntry.objects.create(name='Layout', active=True, project_index_path=0)
        bluesteel_project1 = BluesteelProjectEntry.objects.create(name='Project', order=0, layout=bluesteel_layout1, command_group=command_group, git_project=git_project1)

        bluesteel_layout2 = BluesteelLayoutEntry.objects.create(name='Layout', active=True, project_index_path=0)
        bluesteel_project2 = BluesteelProjectEntry.objects.create(name='Project', order=0, layout=bluesteel_layout2, command_group=command_group, git_project=git_project1)

        benchmark_definition1 = BenchmarkDefinitionEntry.objects.create(name='BenchmarkDefinition1', layout=bluesteel_layout1, project=bluesteel_project1, command_set=command_set, revision=28)

        worker1 = WorkerEntry.objects.create(name='worker-name-1', uuid='uuid-worker-1', operative_system='osx', description='long-description-1', user=user1, git_feeder=False)
        report1 = CommandSetEntry.objects.create(group=None)

        benchmark_execution1 = BenchmarkExecutionEntry.objects.create(definition=benchmark_definition1, commit=commit1, worker=worker1, report=report1, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)

        commands = []
        commands.append('command-new-1')
        commands.append('command-new-2')
        commands.append('command-new-3')
        commands.append('command-new-4')
        commands.append('command-new-5')

        overrides = []
        overrides.append({'result_id' : 'id1', 'override_value' : 28})
        overrides.append({'result_id' : 'id2', 'override_value' : 29})

        self.assertEqual('BenchmarkDefinition1', benchmark_definition1.name)
        self.assertEqual(1, BenchmarkExecutionEntry.objects.all().count())
        self.assertEqual(benchmark_execution1, BenchmarkExecutionEntry.objects.all().first())
        self.assertEqual(0, CommandEntry.objects.filter(command_set=benchmark_definition1.command_set).count())
        self.assertEqual(0, BenchmarkFluctuationOverrideEntry.objects.all().count())

        result = BenchmarkDefinitionController.save_benchmark_definition('BenchmarkDefinition1-1', benchmark_definition1.id, bluesteel_layout2.id, bluesteel_project2.id, True, commands, 28, overrides, 0, [])

        self.assertEqual('BenchmarkDefinition1-1', result.name)
        self.assertEqual(0, BenchmarkExecutionEntry.objects.all().count())

    def test_is_benchmark_definition_equivalent_layout(self):
        layout = BluesteelLayoutEntry.objects.create(name='default-name')
        project = BluesteelProjectController.create_default_project(layout, 'project', 0)
        definition = BenchmarkDefinitionController.create_default_benchmark_definition()

        commands = self.get_default_commands()

        self.assertEqual(False, BenchmarkDefinitionController.is_benchmark_definition_equivalent(definition.id, 2028, project.id, commands))

    def test_is_benchmark_definition_equivalent_project(self):
        layout = BluesteelLayoutEntry.objects.create(name='default-name')
        project = BluesteelProjectController.create_default_project(layout, 'project', 0)
        definition = BenchmarkDefinitionController.create_default_benchmark_definition()

        commands = self.get_default_commands()

        self.assertEqual(False, BenchmarkDefinitionController.is_benchmark_definition_equivalent(definition.id, layout.id, 2028, commands))

    def test_is_benchmark_definition_equivalent_commands(self):
        layout = BluesteelLayoutEntry.objects.create(name='default-name')
        project = BluesteelProjectController.create_default_project(layout, 'project', 0)
        definition = BenchmarkDefinitionController.create_default_benchmark_definition()

        commands = []
        commands.append('command-28')
        commands.append('command-29')
        commands.append('command-30')

        self.assertEqual(False, BenchmarkDefinitionController.is_benchmark_definition_equivalent(definition.id, layout.id, project.id, commands))

    def test_is_benchmark_definition_equivalent_all(self):
        layout = BluesteelLayoutEntry.objects.create(name='default-name')
        project = BluesteelProjectController.create_default_project(layout, 'project', 0)
        definition = BenchmarkDefinitionController.create_default_benchmark_definition()

        commands = self.get_default_commands()

        self.assertEqual(True, BenchmarkDefinitionController.is_benchmark_definition_equivalent(definition.id, layout.id, project.id, commands))

    def test_get_benchmark_definitions_paginated_with_fluctuations(self):
        user1 = User.objects.create_user('user1@test.com', 'user1@test.com', 'pass')
        user1.save()

        git_project1 = GitProjectEntry.objects.create(url='http://test/')

        command_group = CommandGroupEntry.objects.create()
        command_set = CommandSetEntry.objects.create(group=command_group)

        bluesteel_layout = BluesteelLayoutEntry.objects.create(name='Layout', active=True, project_index_path=0)

        bluesteel_project = BluesteelProjectEntry.objects.create(name='Project', order=0, layout=bluesteel_layout, command_group=command_group, git_project=git_project1)

        benchmark_definition1 = BenchmarkDefinitionEntry.objects.create(name='BenchmarkDefinition1', layout=bluesteel_layout, project=bluesteel_project, command_set=command_set, revision=28)
        benchmark_definition2 = BenchmarkDefinitionEntry.objects.create(name='BenchmarkDefinition2', layout=bluesteel_layout, project=bluesteel_project, command_set=command_set, revision=28)
        benchmark_definition3 = BenchmarkDefinitionEntry.objects.create(name='BenchmarkDefinition3', layout=bluesteel_layout, project=bluesteel_project, command_set=command_set, revision=28)
        benchmark_definition4 = BenchmarkDefinitionEntry.objects.create(name='BenchmarkDefinition4', layout=bluesteel_layout, project=bluesteel_project, command_set=command_set, revision=28)
        benchmark_definition5 = BenchmarkDefinitionEntry.objects.create(name='BenchmarkDefinition5', layout=bluesteel_layout, project=bluesteel_project, command_set=command_set, revision=28)
        benchmark_definition6 = BenchmarkDefinitionEntry.objects.create(name='BenchmarkDefinition6', layout=bluesteel_layout, project=bluesteel_project, command_set=command_set, revision=28)

        fluc1 = BenchmarkFluctuationOverrideEntry.objects.create(definition=benchmark_definition1, result_id='id1', override_value=28)
        fluc2 = BenchmarkFluctuationOverrideEntry.objects.create(definition=benchmark_definition2, result_id='id2', override_value=29)
        fluc3 = BenchmarkFluctuationOverrideEntry.objects.create(definition=benchmark_definition2, result_id='id3', override_value=30)

        (definitions1, paginations1) = BenchmarkDefinitionController.get_benchmark_definitions_with_pagination(2, 1, 1)
        definitions1.sort(key=lambda x: x['name'])

        self.assertEqual(2, len(definitions1))
        self.assertEqual('BenchmarkDefinition1', definitions1[0]['name'])
        self.assertEqual(1, len(definitions1[0]['fluctuation_overrides']))
        self.assertEqual('id1', definitions1[0]['fluctuation_overrides'][0]['result_id'])
        self.assertEqual(28, definitions1[0]['fluctuation_overrides'][0]['override_value'])

        self.assertEqual('BenchmarkDefinition2', definitions1[1]['name'])
        self.assertEqual(2, len(definitions1[1]['fluctuation_overrides']))
        self.assertEqual('id2', definitions1[1]['fluctuation_overrides'][0]['result_id'])
        self.assertEqual(29, definitions1[1]['fluctuation_overrides'][0]['override_value'])
        self.assertEqual('id3', definitions1[1]['fluctuation_overrides'][1]['result_id'])
        self.assertEqual(30, definitions1[1]['fluctuation_overrides'][1]['override_value'])

        self.assertEqual(1, paginations1['current'])
        self.assertEqual(1, paginations1['prev'])
        self.assertEqual(2, paginations1['next'])
        self.assertEqual([1, 2, 3], paginations1['page_indices'])


    def test_get_benchmark_definitions_paginated_fist_by_active_then_by_name(self):
        user1 = User.objects.create_user('user1@test.com', 'user1@test.com', 'pass')
        user1.save()

        git_project1 = GitProjectEntry.objects.create(url='http://test/')

        command_group = CommandGroupEntry.objects.create()
        command_set = CommandSetEntry.objects.create(group=command_group)

        bluesteel_layout = BluesteelLayoutEntry.objects.create(name='Layout', active=True, project_index_path=0)

        bluesteel_project = BluesteelProjectEntry.objects.create(name='Project', order=0, layout=bluesteel_layout, command_group=command_group, git_project=git_project1)

        benchmark_definition1 = BenchmarkDefinitionEntry.objects.create(name='BenchmarkDefinition1', layout=bluesteel_layout, project=bluesteel_project, active=True, command_set=command_set, revision=28)
        benchmark_definition2 = BenchmarkDefinitionEntry.objects.create(name='BenchmarkDefinition9', layout=bluesteel_layout, project=bluesteel_project, active=False, command_set=command_set, revision=28)
        benchmark_definition3 = BenchmarkDefinitionEntry.objects.create(name='BenchmarkDefinition2', layout=bluesteel_layout, project=bluesteel_project, active=True, command_set=command_set, revision=28)
        benchmark_definition4 = BenchmarkDefinitionEntry.objects.create(name='BenchmarkDefinition8', layout=bluesteel_layout, project=bluesteel_project, active=False, command_set=command_set, revision=28)
        benchmark_definition5 = BenchmarkDefinitionEntry.objects.create(name='BenchmarkDefinition3', layout=bluesteel_layout, project=bluesteel_project, active=True, command_set=command_set, revision=28)
        benchmark_definition6 = BenchmarkDefinitionEntry.objects.create(name='BenchmarkDefinition7', layout=bluesteel_layout, project=bluesteel_project, active=False, command_set=command_set, revision=28)

        (definitions1, paginations1) = BenchmarkDefinitionController.get_benchmark_definitions_with_pagination(6, 1, 1)

        self.assertEqual(6, len(definitions1))
        self.assertEqual('BenchmarkDefinition1', definitions1[0]['name'])
        self.assertEqual('BenchmarkDefinition2', definitions1[1]['name'])
        self.assertEqual('BenchmarkDefinition3', definitions1[2]['name'])
        self.assertEqual('BenchmarkDefinition7', definitions1[3]['name'])
        self.assertEqual('BenchmarkDefinition8', definitions1[4]['name'])
        self.assertEqual('BenchmarkDefinition9', definitions1[5]['name'])

        self.assertEqual(True,  definitions1[0]['active'])
        self.assertEqual(True,  definitions1[1]['active'])
        self.assertEqual(True,  definitions1[2]['active'])
        self.assertEqual(False, definitions1[3]['active'])
        self.assertEqual(False, definitions1[4]['active'])
        self.assertEqual(False, definitions1[5]['active'])


    def test_populate_worker_passes(self):
        user1 = User.objects.create_user('user1@test.com', 'user1@test.com', 'pass')
        user1.save()

        user2 = User.objects.create_user('user2@test.com', 'user2@test.com', 'pass')
        user2.save()

        git_project1 = GitProjectEntry.objects.create(url='http://test/')

        command_group = CommandGroupEntry.objects.create()
        command_set = CommandSetEntry.objects.create(group=command_group)

        bluesteel_layout = BluesteelLayoutEntry.objects.create(name='Layout', active=True, project_index_path=0)

        bluesteel_project = BluesteelProjectEntry.objects.create(name='Project', order=0, layout=bluesteel_layout, command_group=command_group, git_project=git_project1)

        benchmark_definition1 = BenchmarkDefinitionEntry.objects.create(name='BenchmarkDefinition1', layout=bluesteel_layout, project=bluesteel_project, command_set=command_set, revision=28)

        worker1 = WorkerEntry.objects.create(user=user1)
        worker2 = WorkerEntry.objects.create(user=user2)

        self.assertEqual(0, BenchmarkDefinitionWorkerPassEntry.objects.all().count())

        BenchmarkDefinitionController.populate_worker_passes_for_definition(benchmark_definition1)

        self.assertEqual(2, BenchmarkDefinitionWorkerPassEntry.objects.all().count())
        self.assertEqual(1, BenchmarkDefinitionWorkerPassEntry.objects.filter(definition__id=benchmark_definition1.id, worker__id=worker1.id).count())
        self.assertEqual(1, BenchmarkDefinitionWorkerPassEntry.objects.filter(definition__id=benchmark_definition1.id, worker__id=worker2.id).count())

    def test_populate_worker_passes_with_already_created_ones(self):
        user1 = User.objects.create_user('user1@test.com', 'user1@test.com', 'pass')
        user1.save()

        user2 = User.objects.create_user('user2@test.com', 'user2@test.com', 'pass')
        user2.save()

        git_project1 = GitProjectEntry.objects.create(url='http://test/')

        command_group = CommandGroupEntry.objects.create()
        command_set = CommandSetEntry.objects.create(group=command_group)

        bluesteel_layout = BluesteelLayoutEntry.objects.create(name='Layout', active=True, project_index_path=0)

        bluesteel_project = BluesteelProjectEntry.objects.create(name='Project', order=0, layout=bluesteel_layout, command_group=command_group, git_project=git_project1)

        benchmark_definition1 = BenchmarkDefinitionEntry.objects.create(name='BenchmarkDefinition1', layout=bluesteel_layout, project=bluesteel_project, command_set=command_set, revision=28)
        benchmark_definition2 = BenchmarkDefinitionEntry.objects.create(name='BenchmarkDefinition2', layout=bluesteel_layout, project=bluesteel_project, command_set=command_set, revision=28)

        worker1 = WorkerEntry.objects.create(user=user1)
        worker2 = WorkerEntry.objects.create(user=user2)

        BenchmarkDefinitionWorkerPassEntry.objects.create(definition=benchmark_definition1, worker=worker2)
        BenchmarkDefinitionWorkerPassEntry.objects.create(definition=benchmark_definition2, worker=worker1)

        self.assertEqual(2, BenchmarkDefinitionWorkerPassEntry.objects.all().count())
        self.assertEqual(1, BenchmarkDefinitionWorkerPassEntry.objects.filter(definition__id=benchmark_definition1.id, worker__id=worker2.id).count())
        self.assertEqual(1, BenchmarkDefinitionWorkerPassEntry.objects.filter(definition__id=benchmark_definition2.id, worker__id=worker1.id).count())

        BenchmarkDefinitionController.populate_worker_passes_for_definition(benchmark_definition1)

        self.assertEqual(3, BenchmarkDefinitionWorkerPassEntry.objects.all().count())
        self.assertEqual(1, BenchmarkDefinitionWorkerPassEntry.objects.filter(definition__id=benchmark_definition1.id, worker__id=worker1.id).count())
        self.assertEqual(1, BenchmarkDefinitionWorkerPassEntry.objects.filter(definition__id=benchmark_definition1.id, worker__id=worker2.id).count())
        self.assertEqual(1, BenchmarkDefinitionWorkerPassEntry.objects.filter(definition__id=benchmark_definition2.id, worker__id=worker1.id).count())

        BenchmarkDefinitionController.populate_worker_passes_for_definition(benchmark_definition2)

        self.assertEqual(4, BenchmarkDefinitionWorkerPassEntry.objects.all().count())
        self.assertEqual(1, BenchmarkDefinitionWorkerPassEntry.objects.filter(definition__id=benchmark_definition1.id, worker__id=worker1.id).count())
        self.assertEqual(1, BenchmarkDefinitionWorkerPassEntry.objects.filter(definition__id=benchmark_definition1.id, worker__id=worker2.id).count())
        self.assertEqual(1, BenchmarkDefinitionWorkerPassEntry.objects.filter(definition__id=benchmark_definition2.id, worker__id=worker1.id).count())
        self.assertEqual(1, BenchmarkDefinitionWorkerPassEntry.objects.filter(definition__id=benchmark_definition2.id, worker__id=worker2.id).count())


    def test_populate_worker_passes_for_all_definitions(self):
        user1 = User.objects.create_user('user1@test.com', 'user1@test.com', 'pass')
        user1.save()

        user2 = User.objects.create_user('user2@test.com', 'user2@test.com', 'pass')
        user2.save()

        git_project1 = GitProjectEntry.objects.create(url='http://test/')

        command_group = CommandGroupEntry.objects.create()
        command_set = CommandSetEntry.objects.create(group=command_group)

        bluesteel_layout = BluesteelLayoutEntry.objects.create(name='Layout', active=True, project_index_path=0)

        bluesteel_project = BluesteelProjectEntry.objects.create(name='Project', order=0, layout=bluesteel_layout, command_group=command_group, git_project=git_project1)

        benchmark_definition1 = BenchmarkDefinitionEntry.objects.create(name='BenchmarkDefinition1', layout=bluesteel_layout, project=bluesteel_project, command_set=command_set, revision=28)
        benchmark_definition2 = BenchmarkDefinitionEntry.objects.create(name='BenchmarkDefinition1', layout=bluesteel_layout, project=bluesteel_project, command_set=command_set, revision=28)
        benchmark_definition3 = BenchmarkDefinitionEntry.objects.create(name='BenchmarkDefinition1', layout=bluesteel_layout, project=bluesteel_project, command_set=command_set, revision=28)

        worker1 = WorkerEntry.objects.create(user=user1)
        worker2 = WorkerEntry.objects.create(user=user2)

        self.assertEqual(0, BenchmarkDefinitionWorkerPassEntry.objects.all().count())

        BenchmarkDefinitionController.populate_worker_passes_all_definitions()

        self.assertEqual(6, BenchmarkDefinitionWorkerPassEntry.objects.all().count())
        self.assertEqual(1, BenchmarkDefinitionWorkerPassEntry.objects.filter(definition__id=benchmark_definition1.id, worker__id=worker1.id).count())
        self.assertEqual(1, BenchmarkDefinitionWorkerPassEntry.objects.filter(definition__id=benchmark_definition1.id, worker__id=worker2.id).count())
        self.assertEqual(1, BenchmarkDefinitionWorkerPassEntry.objects.filter(definition__id=benchmark_definition2.id, worker__id=worker1.id).count())
        self.assertEqual(1, BenchmarkDefinitionWorkerPassEntry.objects.filter(definition__id=benchmark_definition2.id, worker__id=worker2.id).count())
        self.assertEqual(1, BenchmarkDefinitionWorkerPassEntry.objects.filter(definition__id=benchmark_definition3.id, worker__id=worker1.id).count())
        self.assertEqual(1, BenchmarkDefinitionWorkerPassEntry.objects.filter(definition__id=benchmark_definition3.id, worker__id=worker2.id).count())


    def test_save_work_passes(self):
        user1 = User.objects.create_user('user1@test.com', 'user1@test.com', 'pass')
        user1.save()

        user2 = User.objects.create_user('user2@test.com', 'user2@test.com', 'pass')
        user2.save()

        git_project1 = GitProjectEntry.objects.create(url='http://test/')

        command_group = CommandGroupEntry.objects.create()
        command_set = CommandSetEntry.objects.create(group=command_group)

        bluesteel_layout = BluesteelLayoutEntry.objects.create(name='Layout', active=True, project_index_path=0)
        bluesteel_project = BluesteelProjectEntry.objects.create(name='Project', order=0, layout=bluesteel_layout, command_group=command_group, git_project=git_project1)

        benchmark_definition1 = BenchmarkDefinitionEntry.objects.create(name='BenchmarkDefinition1', layout=bluesteel_layout, project=bluesteel_project, command_set=command_set, revision=28)
        worker1 = WorkerEntry.objects.create(user=user1)
        worker2 = WorkerEntry.objects.create(user=user2)

        BenchmarkDefinitionWorkerPassEntry.objects.create(definition=benchmark_definition1, worker=worker1, allowed=False)
        BenchmarkDefinitionWorkerPassEntry.objects.create(definition=benchmark_definition1, worker=worker2, allowed=True)

        obj = {}
        obj['work_passes'] = []
        obj['work_passes'].append({'id' : worker1.id, 'allowed' : True})
        obj['work_passes'].append({'id' : worker2.id, 'allowed' : False})

        self.assertEqual(False, BenchmarkDefinitionWorkerPassEntry.objects.filter(worker=worker1).first().allowed)
        self.assertEqual(True, BenchmarkDefinitionWorkerPassEntry.objects.filter(worker=worker2).first().allowed)

        BenchmarkDefinitionController.save_work_passes(obj['work_passes'], benchmark_definition1.id)

        self.assertEqual(True, BenchmarkDefinitionWorkerPassEntry.objects.filter(worker=worker1).first().allowed)
        self.assertEqual(False, BenchmarkDefinitionWorkerPassEntry.objects.filter(worker=worker2).first().allowed)
