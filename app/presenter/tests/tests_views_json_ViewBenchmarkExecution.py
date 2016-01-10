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
from app.logic.gitrepo.models.GitProjectModel import GitProjectEntry
from app.logic.gitrepo.models.GitUserModel import GitUserEntry
from app.logic.gitrepo.models.GitCommitModel import GitCommitEntry
from app.logic.commandrepo.models.CommandModel import CommandEntry
from app.logic.commandrepo.models.CommandResultModel import CommandResultEntry
from app.logic.commandrepo.models.CommandSetModel import CommandSetEntry
from app.logic.commandrepo.models.CommandGroupModel import CommandGroupEntry
from app.logic.bluesteelworker.models.WorkerModel import WorkerEntry
from app.logic.httpcommon import res
import json


class BenchmarkDefinitionViewJsonTestCase(TestCase):

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
                        {'vertical_bars' : {'data' : [1, 2, 3, 4, 5]}}
                    ],
                    'error' : '',
                    'start_time' : str(timezone.now()),
                    'finish_time' : str(timezone.now())
                },
            }]
        }

        self.assertEqual(13, CommandEntry.objects.all().count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git clone http://www.test.com').count())
        self.assertEqual(2, CommandEntry.objects.filter(command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git reset --hard origin/master').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git clean -f -d -q').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git fetch --all').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git pull -r origin master').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git submodule sync').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git submodule update --init --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git pull -r').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-1').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-2').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-3').count())
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
        self.assertEqual(14, CommandEntry.objects.all().count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git clone http://www.test.com').count())
        self.assertEqual(2, CommandEntry.objects.filter(command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git reset --hard origin/master').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git clean -f -d -q').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git fetch --all').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git pull -r origin master').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git submodule sync').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git submodule update --init --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git pull -r').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-1').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-2').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-3').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-vertical-bars').count())
        self.assertEqual(1, CommandResultEntry.objects.all().count())

        obj = json.loads(CommandResultEntry.objects.all().first().out)

        self.assertEqual(1, len(obj))
        self.assertEqual([1, 2, 3, 4, 5], obj[0]['vertical_bars']['data'])


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
                        {'text' : {'data' : 'this is a text, very long'}},
                        {'text' : {'data' : 'this is a text, different'}}
                    ],
                    'error' : '',
                    'start_time' : str(timezone.now()),
                    'finish_time' : str(timezone.now())
                },
            }]
        }

        self.assertEqual(13, CommandEntry.objects.all().count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git clone http://www.test.com').count())
        self.assertEqual(2, CommandEntry.objects.filter(command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git reset --hard origin/master').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git clean -f -d -q').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git fetch --all').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git pull -r origin master').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git submodule sync').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git submodule update --init --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git pull -r').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-1').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-2').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-3').count())
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
        self.assertEqual(14, CommandEntry.objects.all().count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git clone http://www.test.com').count())
        self.assertEqual(2, CommandEntry.objects.filter(command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git reset --hard origin/master').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git clean -f -d -q').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git fetch --all').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git pull -r origin master').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git submodule sync').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git submodule update --init --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git pull -r').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-1').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-2').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-3').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-text').count())
        self.assertEqual(1, CommandResultEntry.objects.all().count())

        obj = json.loads(CommandResultEntry.objects.all().first().out)

        self.assertEqual(2, len(obj))
        self.assertEqual('this is a text, very long', obj[0]['text']['data'])
        self.assertEqual('this is a text, different', obj[1]['text']['data'])

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

        self.assertEqual(13, CommandEntry.objects.all().count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git clone http://www.test.com').count())
        self.assertEqual(2, CommandEntry.objects.filter(command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git reset --hard origin/master').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git clean -f -d -q').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git fetch --all').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git pull -r origin master').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git submodule sync').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git submodule update --init --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git pull -r').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-1').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-2').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-3').count())
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

        self.assertEqual(13, CommandEntry.objects.all().count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git clone http://www.test.com').count())
        self.assertEqual(2, CommandEntry.objects.filter(command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git reset --hard origin/master').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git clean -f -d -q').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git fetch --all').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git pull -r origin master').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git submodule sync').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git submodule update --init --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git pull -r').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-1').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-2').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-3').count())
        self.assertEqual(0, CommandResultEntry.objects.all().count())


