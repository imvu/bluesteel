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
                        {'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1, 2, 3, 4, 5]}
                    ],
                    'error' : '',
                    'start_time' : str(timezone.now()),
                    'finish_time' : str(timezone.now())
                },
            }]
        }

        self.assertEqual(17, CommandEntry.objects.all().count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git clone http://www.test.com').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=0, command='git reset HEAD').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=1, command='git checkout -- .').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=2, command='git clean -d -f -q').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=3, command='git submodule sync --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=4, command='git submodule update --init --recursive --force').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=5, command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=6, command='git reset --hard origin/master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=7, command='git clean -d -f -q').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=8, command='git fetch --all').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=9, command='git pull -r origin master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=10, command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=11, command='git submodule sync --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=12, command='git submodule update --init --recursive --force').count())
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
        self.assertEqual(18, CommandEntry.objects.all().count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git clone http://www.test.com').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=0, command='git reset HEAD').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=1, command='git checkout -- .').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=2, command='git clean -d -f -q').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=3, command='git submodule sync --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=4, command='git submodule update --init --recursive --force').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=5, command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=6, command='git reset --hard origin/master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=7, command='git clean -d -f -q').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=8, command='git fetch --all').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=9, command='git pull -r origin master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=10, command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=11, command='git submodule sync --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=12, command='git submodule update --init --recursive --force').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-1').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-2').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-3').count())
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

        self.assertEqual(17, CommandEntry.objects.all().count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git clone http://www.test.com').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=0, command='git reset HEAD').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=1, command='git checkout -- .').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=2, command='git clean -d -f -q').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=3, command='git submodule sync --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=4, command='git submodule update --init --recursive --force').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=5, command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=6, command='git reset --hard origin/master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=7, command='git clean -d -f -q').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=8, command='git fetch --all').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=9, command='git pull -r origin master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=10, command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=11, command='git submodule sync --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=12, command='git submodule update --init --recursive --force').count())
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
        self.assertEqual(18, CommandEntry.objects.all().count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git clone http://www.test.com').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=0, command='git reset HEAD').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=1, command='git checkout -- .').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=2, command='git clean -d -f -q').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=3, command='git submodule sync --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=4, command='git submodule update --init --recursive --force').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=5, command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=6, command='git reset --hard origin/master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=7, command='git clean -d -f -q').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=8, command='git fetch --all').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=9, command='git pull -r origin master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=10, command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=11, command='git submodule sync --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=12, command='git submodule update --init --recursive --force').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-1').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-2').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-3').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-text').count())
        self.assertEqual(1, CommandResultEntry.objects.all().count())

        obj = json.loads(CommandResultEntry.objects.all().first().out)

        self.assertEqual(2, len(obj))
        self.assertEqual('this is a text, very long', obj[0]['data'])
        self.assertEqual('this is a text, different', obj[1]['data'])

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

        self.assertEqual(17, CommandEntry.objects.all().count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git clone http://www.test.com').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=0, command='git reset HEAD').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=1, command='git checkout -- .').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=2, command='git clean -d -f -q').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=3, command='git submodule sync --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=4, command='git submodule update --init --recursive --force').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=5, command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=6, command='git reset --hard origin/master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=7, command='git clean -d -f -q').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=8, command='git fetch --all').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=9, command='git pull -r origin master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=10, command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=11, command='git submodule sync --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=12, command='git submodule update --init --recursive --force').count())
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

        self.assertEqual(400, resp_obj['status'])

        self.assertEqual(17, CommandEntry.objects.all().count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git clone http://www.test.com').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=0, command='git reset HEAD').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=1, command='git checkout -- .').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=2, command='git clean -d -f -q').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=3, command='git submodule sync --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=4, command='git submodule update --init --recursive --force').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=5, command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=6, command='git reset --hard origin/master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=7, command='git clean -d -f -q').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=8, command='git fetch --all').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=9, command='git pull -r origin master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=10, command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=11, command='git submodule sync --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=12, command='git submodule update --init --recursive --force').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-1').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-2').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-3').count())
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

        self.assertEqual(17, CommandEntry.objects.all().count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git clone http://www.test.com').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=0, command='git reset HEAD').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=1, command='git checkout -- .').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=2, command='git clean -d -f -q').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=3, command='git submodule sync --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=4, command='git submodule update --init --recursive --force').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=5, command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=6, command='git reset --hard origin/master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=7, command='git clean -d -f -q').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=8, command='git fetch --all').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=9, command='git pull -r origin master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=10, command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=11, command='git submodule sync --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=12, command='git submodule update --init --recursive --force').count())
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

        self.assertEqual(17, CommandEntry.objects.all().count())
        self.assertEqual(1, CommandEntry.objects.filter(command='git clone http://www.test.com').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=0, command='git reset HEAD').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=1, command='git checkout -- .').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=2, command='git clean -d -f -q').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=3, command='git submodule sync --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=4, command='git submodule update --init --recursive --force').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=5, command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=6, command='git reset --hard origin/master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=7, command='git clean -d -f -q').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=8, command='git fetch --all').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=9, command='git pull -r origin master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=10, command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=11, command='git submodule sync --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=12, command='git submodule update --init --recursive --force').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-1').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-2').count())
        self.assertEqual(1, CommandEntry.objects.filter(command='command-3').count())
        self.assertEqual(0, CommandResultEntry.objects.all().count())

    def test_notify_benchmark_fluctuation(self):
        commit0 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000000000000000000000000000000000000000', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())
        commit1 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000100001000010000100001000010000100001', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())
        commit2 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000200002000020000200002000020000200002', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())
        commit3 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000300003000030000300003000030000300003', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())
        commit4 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000400004000040000400004000040000400004', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())
        commit5 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000500005000050000500005000050000500005', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())

        branch_test = GitBranchEntry.objects.create(project=self.git_project1, name='branch-test', commit=commit5)
        # GitBranchMergeTargetEntry.objects.create(project=self.git_project1, current_branch=branch2, target_branch=self.branch1, fork_point=self.commit3)

        trail0 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch_test, commit=commit0, order=5)
        trail1 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch_test, commit=commit1, order=4)
        trail2 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch_test, commit=commit2, order=3)
        trail3 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch_test, commit=commit3, order=2)
        trail4 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch_test, commit=commit4, order=1)
        trail5 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch_test, commit=commit5, order=0)

        parent0_1 = GitParentEntry.objects.create(project=self.git_project1, parent=commit0, son=commit1, order=0)
        parent1_2 = GitParentEntry.objects.create(project=self.git_project1, parent=commit1, son=commit2, order=1)
        parent2_3 = GitParentEntry.objects.create(project=self.git_project1, parent=commit2, son=commit3, order=2)
        parent3_4 = GitParentEntry.objects.create(project=self.git_project1, parent=commit3, son=commit4, order=3)
        parent4_5 = GitParentEntry.objects.create(project=self.git_project1, parent=commit4, son=commit5, order=4)

        report_0 = CommandSetEntry.objects.create(group=None)
        report_1 = CommandSetEntry.objects.create(group=None)
        report_2 = CommandSetEntry.objects.create(group=None)
        report_3 = CommandSetEntry.objects.create(group=None)
        report_4 = CommandSetEntry.objects.create(group=None)
        report_5 = CommandSetEntry.objects.create(group=None)

        com0_1 = CommandEntry.objects.create(command_set=report_0, command='command0-1', order=0)
        com1_1 = CommandEntry.objects.create(command_set=report_1, command='command1-1', order=1)
        com2_1 = CommandEntry.objects.create(command_set=report_2, command='command2-1', order=2)
        com3_1 = CommandEntry.objects.create(command_set=report_3, command='command3-1', order=3)
        com4_1 = CommandEntry.objects.create(command_set=report_4, command='command4-1', order=4)
        com5_1 = CommandEntry.objects.create(command_set=report_5, command='command5-1', order=5)

        com0_2 = CommandEntry.objects.create(command_set=report_0, command='command0-2', order=0)
        com1_2 = CommandEntry.objects.create(command_set=report_1, command='command1-2', order=1)
        com2_2 = CommandEntry.objects.create(command_set=report_2, command='command2-2', order=2)
        com3_2 = CommandEntry.objects.create(command_set=report_3, command='command3-2', order=3)
        com4_2 = CommandEntry.objects.create(command_set=report_4, command='command4-2', order=4)
        com5_2 = CommandEntry.objects.create(command_set=report_5, command='command5-2', order=5)

        out_0_1 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1,1,2,3,3]}, {'visual_type' : 'vertical_bars', 'id' : 'id2', 'data' : [1,1,2,3,3]}])
        out_1_1 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1,1,2,3,3]}, {'visual_type' : 'vertical_bars', 'id' : 'id2', 'data' : [1,1,2,3,3]}])
        out_2_1 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1,1,2,3,3]}, {'visual_type' : 'vertical_bars', 'id' : 'id2', 'data' : [1,1,2,3,3]}])
        out_3_1 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1,1,2,3,3]}, {'visual_type' : 'vertical_bars', 'id' : 'id2', 'data' : [1,1,2,3,3]}])
        out_4_1 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [3,3,4,5,5]}, {'visual_type' : 'vertical_bars', 'id' : 'id2', 'data' : [4,4,5,6,6]}])
        out_5_1 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1,1,2,3,3]}, {'visual_type' : 'vertical_bars', 'id' : 'id2', 'data' : [1,1,2,3,3]}])

        out_0_2 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id3', 'data' : [1,1,2,3,3]}, {'visual_type' : 'vertical_bars', 'id' : 'id4', 'data' : [1,1,2,3,3]}])
        out_1_2 = json.dumps([                                                                       {'visual_type' : 'vertical_bars', 'id' : 'id4', 'data' : [1,1,2,3,3]}])
        out_2_2 = json.dumps([                                                                       {'visual_type' : 'vertical_bars', 'id' : 'id4', 'data' : [1,1,2,3,3]}])
        out_3_2 = json.dumps([                                                                       {'visual_type' : 'vertical_bars', 'id' : 'id4', 'data' : [1,1,2,3,3]}])
        out_4_2 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id3', 'data' : [4,4,5,6,6]}, {'visual_type' : 'vertical_bars', 'id' : 'id4', 'data' : [7,7,8,9,9]}])
        out_5_2 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id3', 'data' : [1,1,2,3,3]}, {'visual_type' : 'vertical_bars', 'id' : 'id4', 'data' : [1,1,2,3,3]}])

        CommandResultEntry.objects.create(command=com0_1, out=out_0_1, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com1_1, out=out_1_1, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com2_1, out=out_2_1, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com3_1, out=out_3_1, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com4_1, out=out_4_1, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com5_1, out=out_5_1, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())

        CommandResultEntry.objects.create(command=com0_2, out=out_0_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com1_2, out=out_1_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com2_2, out=out_2_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com3_2, out=out_3_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com4_2, out=out_4_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())
        CommandResultEntry.objects.create(command=com5_2, out=out_5_2, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())

        benchmark_execution0 = BenchmarkExecutionEntry.objects.create(definition=self.benchmark_definition1, commit=commit0, worker=self.worker1, report=report_0, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)
        benchmark_execution1 = BenchmarkExecutionEntry.objects.create(definition=self.benchmark_definition1, commit=commit1, worker=self.worker1, report=report_1, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)
        benchmark_execution2 = BenchmarkExecutionEntry.objects.create(definition=self.benchmark_definition1, commit=commit2, worker=self.worker1, report=report_2, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)
        benchmark_execution3 = BenchmarkExecutionEntry.objects.create(definition=self.benchmark_definition1, commit=commit3, worker=self.worker1, report=report_3, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)
        benchmark_execution4 = BenchmarkExecutionEntry.objects.create(definition=self.benchmark_definition1, commit=commit4, worker=self.worker1, report=report_4, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)
        benchmark_execution5 = BenchmarkExecutionEntry.objects.create(definition=self.benchmark_definition1, commit=commit5, worker=self.worker1, report=report_5, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)

        ViewJsonBenchmarkExecutions.notify_benchmark_fluctuation(benchmark_execution4, 2, 'test-domain.com')

        self.assertEqual(1, StackedMailEntry.objects.all().count())
        self.assertEqual('Benchmark execution fluctuation on commit: 0000400004000040000400004000040000400004', StackedMailEntry.objects.all().first().title)
        self.assertEqual('user1@test.com', StackedMailEntry.objects.all().first().receiver)
        self.assertTrue('http://test-domain.com/main/execution/{0}/window/'.format(benchmark_execution4.id) in StackedMailEntry.objects.all().first().content)

    def test_notify_benchmark_fluctuation(self):
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


        report = CommandSetEntry.objects.create(group=None)
        benchmark_execution = BenchmarkExecutionEntry.objects.create(definition=self.benchmark_definition1, commit=self.commit1, worker=self.worker1, report=report, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)

        ViewJsonBenchmarkExecutions.notify_benchmark_command_failure(benchmark_execution, report_json, 'test-domain.com')

        self.assertEqual(1, StackedMailEntry.objects.all().count())
        self.assertEqual('Benchmark execution with failed commands on commit: 0000100001000010000100001000010000100001', StackedMailEntry.objects.all().first().title)
        self.assertEqual('user1@test.com', StackedMailEntry.objects.all().first().receiver)
        self.assertTrue('http://test-domain.com/main/execution/{0}/'.format(benchmark_execution.id) in StackedMailEntry.objects.all().first().content)
