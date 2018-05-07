""" Presenter Views BenchmarkExecution tests """

from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from django.utils import timezone
from app.logic.benchmark.controllers.BenchmarkDefinitionController import BenchmarkDefinitionController
from app.logic.benchmark.controllers.BenchmarkExecutionController import BenchmarkExecutionController
from app.logic.bluesteel.controllers.BluesteelLayoutController import BluesteelLayoutController
from app.logic.bluesteel.controllers.BluesteelProjectController import BluesteelProjectController
from app.logic.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.logic.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.logic.benchmark.models.BenchmarkExecutionModel import BenchmarkExecutionEntry
from app.logic.benchmark.models.BenchmarkFluctuationWaiverModel import BenchmarkFluctuationWaiverEntry
from app.logic.gitrepo.models.GitProjectModel import GitProjectEntry
from app.logic.gitrepo.models.GitUserModel import GitUserEntry
from app.logic.gitrepo.models.GitCommitModel import GitCommitEntry
from app.logic.gitrepo.models.GitBranchModel import GitBranchEntry
from app.logic.gitrepo.models.GitBranchTrailModel import GitBranchTrailEntry
from app.logic.gitrepo.models.GitParentModel import GitParentEntry
from app.logic.commandrepo.models.CommandModel import CommandEntry
from app.logic.commandrepo.models.CommandResultModel import CommandResultEntry
from app.logic.commandrepo.models.CommandSetModel import CommandSetEntry
from app.logic.commandrepo.models.CommandGroupModel import CommandGroupEntry
from app.logic.bluesteelworker.models.WorkerModel import WorkerEntry
from app.logic.mailing.models.StackedMailModel import StackedMailEntry
from app.logic.httpcommon import res
from app.presenter.views.json import ViewJsonBenchmarkExecutions
import json


class BenchmarkExecutionViewJsonTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user('user1@test.com', 'user1@test.com', 'pass')

        self.git_project1 = GitProjectEntry.objects.create(url='http://test/')

        self.git_user1 = GitUserEntry.objects.create(
            project=self.git_project1,
            name='user1',
            email='user1@test.com'
        )

        self.commit1 = GitCommitEntry.objects.create(
            project=self.git_project1,
            commit_hash='0000100001000010000100001000010000100001',
            author=self.git_user1,
            author_date=timezone.now(),
            committer=self.git_user1,
            committer_date=timezone.now()
        )

        self.worker1 = WorkerEntry.objects.create(
            name='worker-name-1',
            uuid='uuid-worker-1',
            operative_system='osx',
            description='long-description-1',
            user=self.user1,
            git_feeder=False
        )

        self.bluesteel_layout1 = BluesteelLayoutController.create_new_default_layout()
        self.benchmark_definition1 = BenchmarkDefinitionController.create_default_benchmark_definition()

    def tearDown(self):
        pass

    def check_default_fetch_commands(self):
        self.assertEqual(1, CommandEntry.objects.filter(order=0, command='git reset HEAD').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=1, command='git checkout -- .').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=2, command='git clean -d -f -q').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=3, command='git submodule sync --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=4, command='git submodule update --init --recursive --force').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=5, command='git submodule foreach --recursive git clean -x -d -f -q').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=6, command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=7, command='git reset --hard origin/master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=8, command='git clean -d -f -q').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=9, command='git fetch --all -p').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=10, command='git pull -r origin master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=11, command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=12, command='git submodule sync --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=13, command='git submodule update --init --recursive --force').count())
        return True

    def test_save_benchmark_execution_id_too_long(self):
        execution = BenchmarkExecutionController.create_benchmark_execution(
            self.benchmark_definition1,
            self.commit1,
            self.worker1)

        long_id = 'a' * 256

        obj = {
            'command_set' : [{
                'command' : 'command-vertical-bars',
                'result' : {
                    'status' : 0,
                    'out' : [
                        {'visual_type' : 'vertical_bars', 'id' : long_id, 'data' : []}
                    ],
                    'error' : '',
                    'start_time' : str(timezone.now()),
                    'finish_time' : str(timezone.now())
                },
            }]
        }

        resp = self.client.post(
            '/main/execution/{0}/save/'.format(execution.id),
            data = json.dumps(obj),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(406, resp_obj['status'])


    def test_save_benchmark_execution_vertical_bars(self):
        execution = BenchmarkExecutionController.create_benchmark_execution(
            self.benchmark_definition1,
            self.commit1,
            self.worker1)

        obj = {
            'command_set' : [{
                'command' : 'command-vertical-bars',
                'result' : {
                    'status' : 0,
                    'out' : [
                        {'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1, 2, 3, 4, 5]}
                    ],
                    'error' : '',
                    'start_time' : str(timezone.now()),
                    'finish_time' : str(timezone.now())
                },
            }]
        }

        self.assertEqual(18, CommandEntry.objects.all().count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git clone http://www.test.com').count())
        self.assertTrue(self.check_default_fetch_commands())
        self.assertEqual(1, CommandEntry.objects.filter(command='git checkout {commit_hash}').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git submodule update --init --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='<add_more_commands_here>').count())

        self.assertEqual(0, CommandResultEntry.objects.all().count())

        resp = self.client.post(
            '/main/execution/{0}/save/'.format(execution.id),
            data = json.dumps(obj),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])

        execution = BenchmarkExecutionEntry.objects.filter(definition=self.benchmark_definition1).first()

        self.assertEqual('command-vertical-bars', CommandEntry.objects.filter(command_set=execution.report).first().command)
        self.assertEqual(19, CommandEntry.objects.all().count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git clone http://www.test.com').count())
        self.assertTrue(self.check_default_fetch_commands())
        self.assertEqual(1, CommandEntry.objects.filter(command='git checkout {commit_hash}').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git submodule update --init --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='<add_more_commands_here>').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-vertical-bars').count())
        self.assertEqual(1, CommandResultEntry.objects.all().count())

        obj = json.loads(CommandResultEntry.objects.all().first().out)

        self.assertEqual(1, len(obj))
        self.assertEqual([1, 2, 3, 4, 5], obj[0]['data'])


    def test_save_benchmark_execution_text(self):
        execution = BenchmarkExecutionController.create_benchmark_execution(
            self.benchmark_definition1,
            self.commit1,
            self.worker1)

        obj = {
            'command_set' : [{
                'command' : 'command-text',
                'result' : {
                    'status' : 0,
                    'out' : [
                        {'visual_type' : 'text', 'id' : 'id1', 'data' : 'this is a text, very long'},
                        {'visual_type' : 'text', 'id' : 'id2', 'data' : 'this is a text, different'}
                    ],
                    'error' : '',
                    'start_time' : str(timezone.now()),
                    'finish_time' : str(timezone.now())
                },
            }]
        }

        self.assertEqual(18, CommandEntry.objects.all().count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git clone http://www.test.com').count())
        self.assertTrue(self.check_default_fetch_commands())
        self.assertEqual(1, CommandEntry.objects.filter(command='git checkout {commit_hash}').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git submodule update --init --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='<add_more_commands_here>').count())
        self.assertEqual(0, CommandResultEntry.objects.all().count())

        resp = self.client.post(
            '/main/execution/{0}/save/'.format(execution.id),
            data = json.dumps(obj),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])

        execution = BenchmarkExecutionEntry.objects.filter(definition=self.benchmark_definition1).first()

        self.assertEqual('command-text', CommandEntry.objects.filter(command_set=execution.report).first().command)
        self.assertEqual(19, CommandEntry.objects.all().count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git clone http://www.test.com').count())
        self.assertTrue(self.check_default_fetch_commands())
        self.assertEqual(1, CommandEntry.objects.filter(command='git checkout {commit_hash}').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git submodule update --init --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='<add_more_commands_here>').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-text').count())
        self.assertEqual(1, CommandResultEntry.objects.all().count())

        obj = json.loads(CommandResultEntry.objects.all().first().out)

        self.assertEqual(2, len(obj))
        self.assertEqual('this is a text, very long', obj[0]['data'])
        self.assertEqual('this is a text, different', obj[1]['data'])

    def test_save_benchmark_execution_unknown(self):
        execution = BenchmarkExecutionController.create_benchmark_execution(
            self.benchmark_definition1,
            self.commit1,
            self.worker1)

        obj = {
            'command_set' : [{
                'command' : 'command-unknown',
                'result' : {
                    'status' : 0,
                    'out' : [
                        {'visual_type' : 'unknown', 'id' : 'id1', 'data' : 'this is an unknown text, very long'},
                        {'visual_type' : 'unknown', 'id' : 'id2', 'data' : 'this is an unknown text, different'}
                    ],
                    'error' : '',
                    'start_time' : str(timezone.now()),
                    'finish_time' : str(timezone.now())
                },
            }]
        }

        self.assertEqual(18, CommandEntry.objects.all().count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git clone http://www.test.com').count())
        self.assertTrue(self.check_default_fetch_commands())
        self.assertEqual(1, CommandEntry.objects.filter(command='git checkout {commit_hash}').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git submodule update --init --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='<add_more_commands_here>').count())
        self.assertEqual(0, CommandResultEntry.objects.all().count())

        resp = self.client.post(
            '/main/execution/{0}/save/'.format(execution.id),
            data = json.dumps(obj),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])

        execution = BenchmarkExecutionEntry.objects.filter(definition=self.benchmark_definition1).first()

        self.assertEqual('command-unknown', CommandEntry.objects.filter(command_set=execution.report).first().command)
        self.assertEqual(19, CommandEntry.objects.all().count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git clone http://www.test.com').count())
        self.assertTrue(self.check_default_fetch_commands())
        self.assertEqual(1, CommandEntry.objects.filter(command='git checkout {commit_hash}').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git submodule update --init --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='<add_more_commands_here>').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-unknown').count())
        self.assertEqual(1, CommandResultEntry.objects.all().count())

        obj = json.loads(CommandResultEntry.objects.all().first().out)

        self.assertEqual(2, len(obj))
        self.assertEqual('this is an unknown text, very long', obj[0]['data'])
        self.assertEqual('this is an unknown text, different', obj[1]['data'])


    def test_save_benchmark_stores_the_correct_json(self):
        execution = BenchmarkExecutionController.create_benchmark_execution(
            self.benchmark_definition1,
            self.commit1,
            self.worker1)

        obj = {
            'command_set' : [{
                'command' : 'command-vertical-bars',
                'result' : {
                    'status' : 0,
                    'out' : [
                        {'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1, 2, 3, 4, 5]},
                        {'visual_type' : 'text', 'id' : 'id2', 'data' : 'this is a text, very long'}
                    ],
                    'error' : '',
                    'start_time' : str(timezone.now()),
                    'finish_time' : str(timezone.now())
                },
            }]
        }

        resp = self.client.post(
            '/main/execution/{0}/save/'.format(execution.id),
            data = json.dumps(obj),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])

        execution = BenchmarkExecutionEntry.objects.filter(definition=self.benchmark_definition1).first()
        obj = json.loads(CommandResultEntry.objects.all().first().out)

        self.assertEqual(2, len(obj))
        self.assertEqual('id1', obj[0]['id'])
        self.assertEqual('vertical_bars', obj[0]['visual_type'])
        self.assertEqual([1, 2, 3, 4, 5], obj[0]['data'])
        self.assertEqual('id2', obj[1]['id'])
        self.assertEqual('text', obj[1]['visual_type'])
        self.assertEqual('this is a text, very long', obj[1]['data'])

    def test_save_fails_because_same_id_found_on_out_data(self):
        execution = BenchmarkExecutionController.create_benchmark_execution(
            self.benchmark_definition1,
            self.commit1,
            self.worker1)

        obj = {
            'command_set' : [{
                'command' : 'command-text',
                'result' : {
                    'status' : 0,
                    'out' : [
                        {'visual_type' : 'text', 'id' : 'id1', 'data' : 'this is a text, very long'},
                        {'visual_type' : 'text', 'id' : 'id2', 'data' : 'this is a text, different1'},
                        {'visual_type' : 'text', 'id' : 'id3', 'data' : 'this is a text, different2'},
                        {'visual_type' : 'text', 'id' : 'id1', 'data' : 'this is a text, different3'}
                    ],
                    'error' : '',
                    'start_time' : str(timezone.now()),
                    'finish_time' : str(timezone.now())
                },
            }]
        }

        self.assertEqual(18, CommandEntry.objects.all().count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git clone http://www.test.com').count())
        self.assertTrue(self.check_default_fetch_commands())
        self.assertEqual(1, CommandEntry.objects.filter(command='git checkout {commit_hash}').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git submodule update --init --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='<add_more_commands_here>').count())
        self.assertEqual(0, CommandResultEntry.objects.all().count())

        resp = self.client.post(
            '/main/execution/{0}/save/'.format(execution.id),
            data = json.dumps(obj),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(400, resp_obj['status'])

        self.assertEqual(18, CommandEntry.objects.all().count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git clone http://www.test.com').count())
        self.assertTrue(self.check_default_fetch_commands())
        self.assertEqual(1, CommandEntry.objects.filter(command='git checkout {commit_hash}').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git submodule update --init --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='<add_more_commands_here>').count())
        self.assertEqual(0, CommandResultEntry.objects.all().count())


    def test_save_benchmark_execution_no_recognized(self):
        execution = BenchmarkExecutionController.create_benchmark_execution(
            self.benchmark_definition1,
            self.commit1,
            self.worker1)

        obj = {
            'command_set' : [{
                'command' : 'command-text',
                'result' : {
                    'status' : 0,
                    'out' : [
                        {'other-thing' : 'not-recognized'}
                    ],
                    'error' : '',
                    'start_time' : str(timezone.now()),
                    'finish_time' : str(timezone.now())
                },
            }]
        }

        self.assertEqual(18, CommandEntry.objects.all().count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git clone http://www.test.com').count())
        self.assertTrue(self.check_default_fetch_commands())
        self.assertEqual(1, CommandEntry.objects.filter(command='git checkout {commit_hash}').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git submodule update --init --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='<add_more_commands_here>').count())
        self.assertEqual(0, CommandResultEntry.objects.all().count())

        resp = self.client.post(
            '/main/execution/{0}/save/'.format(execution.id),
            data = json.dumps(obj),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(406, resp_obj['status'])
        self.assertEqual('Schema failed.', resp_obj['message'])

        execution = BenchmarkExecutionEntry.objects.filter(definition=self.benchmark_definition1).first()

        self.assertEqual(19, CommandEntry.objects.all().count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git clone http://www.test.com').count())
        self.assertTrue(self.check_default_fetch_commands())
        self.assertEqual(1, CommandEntry.objects.filter(command='git checkout {commit_hash}').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git submodule update --init --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='<add_more_commands_here>').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='Problem while saving benchmark execution!').count())
        self.assertEqual(1, CommandResultEntry.objects.all().count())
        self.assertEqual(-1, CommandResultEntry.objects.all().first().status)

    def test_did_commands_succeed(self):
        com1 = {}
        com1['command'] = 'command-1'
        com1['result'] = {}
        com1['result']['status'] = 0
        com1['result']['out'] = 'out-1'
        com1['result']['error'] = 'error-1'

        com2 = {}
        com2['command'] = 'command-2'
        com2['result'] = {}
        com2['result']['status'] = -1
        com2['result']['out'] = 'out-2'
        com2['result']['error'] = 'error-2'

        report_json = {}
        report_json['command_set'] = []
        report_json['command_set'].append(com1)
        report_json['command_set'].append(com2)

        self.assertEqual(False, ViewJsonBenchmarkExecutions.did_commands_succeed(report_json))


    def test_notification_email_if_json_is_not_valid(self):
        execution = BenchmarkExecutionController.create_benchmark_execution(
            self.benchmark_definition1,
            self.commit1,
            self.worker1)

        resp = self.client.post(
            '/main/execution/{0}/save/'.format(execution.id),
            data = 'this-is-not-a-json-string',
            content_type='application/json')

        self.assertEqual(1, StackedMailEntry.objects.all().count())
        self.assertEqual('Json invalid', StackedMailEntry.objects.all().first().title)
        self.assertEqual('user1@test.com', StackedMailEntry.objects.all().first().receiver)
        self.assertTrue('this-is-not-a-json-string' in StackedMailEntry.objects.all().first().content)

    def test_notification_email_if_json_schema_failure(self):
        execution = BenchmarkExecutionController.create_benchmark_execution(
            self.benchmark_definition1,
            self.commit1,
            self.worker1)

        resp = self.client.post(
            '/main/execution/{0}/save/'.format(execution.id),
            data = json.dumps({}),
            content_type='application/json')

        self.assertEqual(1, StackedMailEntry.objects.all().count())
        self.assertEqual('Schema failed notification', StackedMailEntry.objects.all().first().title)
        self.assertEqual('user1@test.com', StackedMailEntry.objects.all().first().receiver)

    def test_fluctuation_waiver_modified_successfully_to_true(self):
        waiver = BenchmarkFluctuationWaiverEntry.objects.create(git_user=self.git_user1, notification_allowed=False)

        self.assertEqual(1, BenchmarkFluctuationWaiverEntry.objects.all().count())
        self.assertEqual(1, BenchmarkFluctuationWaiverEntry.objects.filter(git_user__id=self.git_user1.id, notification_allowed=False).count())

        resp = self.client.post(
            '/main/notification/waiver/{0}/allow/'.format(waiver.id),
            data = json.dumps({}),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual(1, BenchmarkFluctuationWaiverEntry.objects.all().count())
        self.assertEqual(1, BenchmarkFluctuationWaiverEntry.objects.filter(git_user__id=self.git_user1.id, notification_allowed=True).count())

    def test_fluctuation_waiver_modified_successfully_to_false(self):
        waiver = BenchmarkFluctuationWaiverEntry.objects.create(git_user=self.git_user1, notification_allowed=True)

        self.assertEqual(1, BenchmarkFluctuationWaiverEntry.objects.all().count())
        self.assertEqual(1, BenchmarkFluctuationWaiverEntry.objects.filter(git_user__id=self.git_user1.id, notification_allowed=True).count())

        resp = self.client.post(
            '/main/notification/waiver/{0}/deny/'.format(waiver.id),
            data = json.dumps({}),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual(1, BenchmarkFluctuationWaiverEntry.objects.all().count())
        self.assertEqual(1, BenchmarkFluctuationWaiverEntry.objects.filter(git_user__id=self.git_user1.id, notification_allowed=False).count())

    def test_fluctuation_waiver_modified_not_successful(self):
        resp = self.client.post(
            '/main/notification/waiver/28/deny/',
            data = json.dumps({}),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(404, resp_obj['status'])
