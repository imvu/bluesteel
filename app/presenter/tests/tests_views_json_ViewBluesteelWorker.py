""" View git repo tests """

from django.test import TestCase
from django.test import Client
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from app.logic.httpcommon import res
from app.logic.bluesteelworker.models.WorkerModel import WorkerEntry
from app.logic.bluesteelworker.models.WorkerFilesHashModel import WorkerFilesHashEntry
from app.logic.benchmark.models.BenchmarkExecutionModel import BenchmarkExecutionEntry
from app.logic.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.logic.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.logic.gitrepo.models.GitProjectModel import GitProjectEntry
from app.logic.gitrepo.models.GitCommitModel import GitCommitEntry
from app.logic.gitrepo.models.GitUserModel import GitUserEntry
from app.logic.commandrepo.models.CommandGroupModel import CommandGroupEntry
from app.logic.commandrepo.models.CommandSetModel import CommandSetEntry
from datetime import timedelta
import json
import StringIO
import zipfile

class ViewsBluesteelWorkerTestCase(TestCase):

    def setUp(self):
        self.client = Client()

        self.user1 = User.objects.create_user('user1@test.com', 'user1@test.com', 'pass1')
        self.user2 = User.objects.create_user('user2@test.com', 'user2@test.com', 'pass2')

        self.worker_1 = WorkerEntry.objects.create(
            name='worker-1',
            uuid='8a88432d-33db-4d24-a0a7-2f863e7e8e4a',
            description='One Worker :)',
            user=self.user1
        )

        self.git_project1 = GitProjectEntry.objects.create(url='http://test/')
        self.git_user1 = GitUserEntry.objects.create(
            project=self.git_project1,
            name='user1',
            email='user1@test.com'
        )

    def tearDown(self):
        pass

    def test_download_worker(self):
        resp = self.client.get('/main/bluesteelworker/download/')

        self.assertEquals('attachment; filename=BluesteelWorker.zip', resp.get('Content-Disposition'))

        f = StringIO.StringIO(resp.content)
        zipped_file = zipfile.ZipFile(f, 'r')

        self.assertIsNone(zipped_file.testzip())
        self.assertIn('__init__.py', zipped_file.namelist())
        self.assertIn('core/__init__.py', zipped_file.namelist())
        self.assertIn('core/GitFetcher.py', zipped_file.namelist())
        self.assertIn('core/Request.py', zipped_file.namelist())
        self.assertIn('core/settings.json', zipped_file.namelist())
        self.assertIn('core/Worker.py', zipped_file.namelist())

        settings_file = zipped_file.open('core/settings.json', 'r')
        settings = settings_file.read()
        obj = json.loads(settings)

        self.assertEqual('http://testserver/main/bluesteelworker/bootstrap/', obj['entry_point'])
        self.assertEqual(['..', 'tmp', 'worker_tmp'], obj['tmp_path'])

        settings_file.close()
        zipped_file.close()
        f.close()

    def test_get_bootstrap_urls(self):
        resp = self.client.get('/main/bluesteelworker/bootstrap/')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual('http://testserver/main/layout/all/urls/', resp_obj['data']['layouts_url'])
        self.assertEqual('http://testserver/main/bluesteelworker/', resp_obj['data']['worker_info_url'])
        self.assertEqual('http://testserver/main/bluesteelworker/create/', resp_obj['data']['create_worker_url'])
        self.assertEqual('http://testserver/main/bluesteelworker/login/', resp_obj['data']['login_worker_url'])

    def test_get_worker_info(self):
        resp = self.client.get('/main/bluesteelworker/8a88432d-33db-4d24-a0a7-2f863e7e8e4a/')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual('worker-1', resp_obj['data']['worker']['name'])
        self.assertEqual('8a88432d-33db-4d24-a0a7-2f863e7e8e4a', resp_obj['data']['worker']['uuid'])
        self.assertEqual('One Worker :)', resp_obj['data']['worker']['description'])
        self.assertEqual('http://testserver/main/bluesteelworker/8a88432d-33db-4d24-a0a7-2f863e7e8e4a/', resp_obj['data']['worker']['url']['worker_info_full'])
        self.assertEqual('http://testserver/main/bluesteelworker/1/update/activity/', resp_obj['data']['worker']['url']['update_activity_point'])

    def test_get_worker_info_not_found(self):
        resp = self.client.get('/main/bluesteelworker/8a88432d-33db-4d24-a0a7-20000000000a/')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(400, resp_obj['status'])
        self.assertEqual('Worker not found', resp_obj['message'])

    def test_create_new_worker_that_does_not_exists_yet(self):
        self.assertEqual(0, BenchmarkExecutionEntry.objects.all().count())

        post_data = {}
        post_data['uuid'] = '8a88432d-33db-4d24-a0a7-0000007e8e4a'
        post_data['operative_system'] = 'osx'
        post_data['host_name'] = 'host-name'

        post_str = json.dumps(post_data)

        resp = self.client.post(
            '/main/bluesteelworker/create/',
            data=post_str,
            content_type='text/plain'
        )

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual('8a88432d-33db-4d24-a0a7-0000007e8e4a', resp_obj['data']['worker']['uuid'])
        self.assertEqual('osx', resp_obj['data']['worker']['operative_system'])
        self.assertEqual('host-name', resp_obj['data']['worker']['name'])
        self.assertEqual('http://testserver/main/bluesteelworker/2/update/activity/', resp_obj['data']['worker']['url']['update_activity_point'])

        entry = WorkerEntry.objects.all().filter(id=resp_obj['data']['worker']['id']).first()

        self.assertEqual('8a88432d-33db-4d24-a0a7-0000007e8e4a', entry.uuid)
        self.assertEqual('osx', entry.operative_system)
        self.assertEqual('host-name', entry.name)

        user_entry = User.objects.all().filter(id=entry.user.id).first()

        self.assertEqual('8a88432d-33db-4d24-a0a7-000000', user_entry.username)
        self.assertEqual(0, BenchmarkExecutionEntry.objects.all().count())

    def test_firsst_created_worker_is_git_feeder_by_default(self):
        self.worker_1.delete()
        self.assertEqual(0, WorkerEntry.objects.all().count())

        post_data1 = {}
        post_data1['uuid'] = '8a88432d-33db-4d24-a0a7-0000007e8e4a'
        post_data1['operative_system'] = 'osx'
        post_data1['host_name'] = 'host-name-1'

        post_data2 = {}
        post_data2['uuid'] = '8a88432d-33db-4d24-a0a7-000000111111'
        post_data2['operative_system'] = 'linux'
        post_data2['host_name'] = 'host-name-2'

        post_str1 = json.dumps(post_data1)
        post_str2 = json.dumps(post_data2)

        resp1 = self.client.post(
            '/main/bluesteelworker/create/',
            data=post_str1,
            content_type='text/plain'
        )

        res.check_cross_origin_headers(self, resp1)
        resp1_obj = json.loads(resp1.content)

        self.assertEqual(200, resp1_obj['status'])
        self.assertEqual('8a88432d-33db-4d24-a0a7-0000007e8e4a', resp1_obj['data']['worker']['uuid'])
        self.assertEqual('osx', resp1_obj['data']['worker']['operative_system'])
        self.assertEqual('host-name-1', resp1_obj['data']['worker']['name'])
        self.assertEqual('http://testserver/main/bluesteelworker/2/update/activity/', resp1_obj['data']['worker']['url']['update_activity_point'])

        entry1 = WorkerEntry.objects.all().filter(id=resp1_obj['data']['worker']['id']).first()

        self.assertEqual('8a88432d-33db-4d24-a0a7-0000007e8e4a', entry1.uuid)
        self.assertEqual('osx', entry1.operative_system)
        self.assertEqual('host-name-1', entry1.name)
        self.assertEqual(True, entry1.git_feeder)

        resp2 = self.client.post(
            '/main/bluesteelworker/create/',
            data=post_str2,
            content_type='text/plain'
        )

        res.check_cross_origin_headers(self, resp2)
        resp2_obj = json.loads(resp2.content)

        self.assertEqual(200, resp2_obj['status'])
        self.assertEqual('8a88432d-33db-4d24-a0a7-000000111111', resp2_obj['data']['worker']['uuid'])
        self.assertEqual('linux', resp2_obj['data']['worker']['operative_system'])
        self.assertEqual('host-name-2', resp2_obj['data']['worker']['name'])
        self.assertEqual('http://testserver/main/bluesteelworker/3/update/activity/', resp2_obj['data']['worker']['url']['update_activity_point'])

        entry2 = WorkerEntry.objects.all().filter(id=resp2_obj['data']['worker']['id']).first()

        self.assertEqual('8a88432d-33db-4d24-a0a7-000000111111', entry2.uuid)
        self.assertEqual('linux', entry2.operative_system)
        self.assertEqual('host-name-2', entry2.name)
        self.assertEqual(False, entry2.git_feeder)


    def test_create_new_worker_also_creates_benchmark_executions(self):
        command_group = CommandGroupEntry.objects.create()
        command_set = CommandSetEntry.objects.create(
            group=command_group
        )

        git_commit1 = GitCommitEntry.objects.create(
            project=self.git_project1,
            commit_hash='0000100001000010000100001000010000100001',
            author=self.git_user1,
            author_date=timezone.now(),
            committer=self.git_user1,
            committer_date=timezone.now()
        )

        git_commit2 = GitCommitEntry.objects.create(
            project=self.git_project1,
            commit_hash='0000200002000020000200002000020000200002',
            author=self.git_user1,
            author_date=timezone.now(),
            committer=self.git_user1,
            committer_date=timezone.now()
        )

        bluesteel_layout = BluesteelLayoutEntry.objects.create(
            name='Layout',
            active=True,
            project_index_path=0,
        )

        bluesteel_project = BluesteelProjectEntry.objects.create(
            name='Project',
            order=0,
            layout=bluesteel_layout,
            command_group=command_group,
            git_project=self.git_project1,
        )

        benchmark_definition1 = BenchmarkDefinitionEntry.objects.create(
            name='BenchmarkDefinition1',
            layout=bluesteel_layout,
            project=bluesteel_project,
            command_set=command_set,
            revision=28,
        )

        benchmark_definition2 = BenchmarkDefinitionEntry.objects.create(
            name='BenchmarkDefinition2',
            layout=bluesteel_layout,
            project=bluesteel_project,
            command_set=command_set,
            revision=3,
        )

        post_data = {}
        post_data['uuid'] = '8a88432d-33db-4d24-a0a7-0000007e8e4a'
        post_data['operative_system'] = 'osx'
        post_data['host_name'] = 'host-name'

        post_str = json.dumps(post_data)

        self.assertEqual(0, BenchmarkExecutionEntry.objects.all().count())

        resp = self.client.post(
            '/main/bluesteelworker/create/',
            data=post_str,
            content_type='text/plain'
        )

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual('8a88432d-33db-4d24-a0a7-0000007e8e4a', resp_obj['data']['worker']['uuid'])
        self.assertEqual('osx', resp_obj['data']['worker']['operative_system'])
        self.assertEqual('host-name', resp_obj['data']['worker']['name'])
        self.assertEqual('http://testserver/main/bluesteelworker/2/update/activity/', resp_obj['data']['worker']['url']['update_activity_point'])

        entry = WorkerEntry.objects.all().filter(id=resp_obj['data']['worker']['id']).first()

        self.assertEqual('8a88432d-33db-4d24-a0a7-0000007e8e4a', entry.uuid)
        self.assertEqual('osx', entry.operative_system)
        self.assertEqual('host-name', entry.name)

        user_entry = User.objects.all().filter(id=entry.user.id).first()

        self.assertEqual('8a88432d-33db-4d24-a0a7-000000', user_entry.username)
        self.assertEqual(4, BenchmarkExecutionEntry.objects.all().count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(definition=benchmark_definition1, commit=git_commit1, worker=entry).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(definition=benchmark_definition1, commit=git_commit2, worker=entry).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(definition=benchmark_definition2, commit=git_commit1, worker=entry).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(definition=benchmark_definition2, commit=git_commit2, worker=entry).count())


    def test_login_worker_with_correct_password(self):
        post_data = {}
        post_data['username'] = '8a88432d-33db-4d24-a0a7-2f863e'
        post_data['password'] = '8a88432d-33db-4d24-a0a7-2f863e7e8e4a'

        user1 = User.objects.create_user(post_data['username'], None, post_data['password'])
        user1.save()

        worker = WorkerEntry.objects.create(
            name='worker-1',
            uuid=post_data['username'],
            description='One Worker :)',
            user=user1
        )

        resp = self.client.post(
            '/main/bluesteelworker/login/',
            data=json.dumps(post_data),
            content_type='text/plain'
        )

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual('Access granted!', resp_obj['message'])
        self.assertEqual(user1.id, int(self.client.session['_auth_user_id']))

    def test_login_worker_with_long_password_also_succeeds(self):
        post_data = {}
        post_data['username'] = '8a88432d-33db-4d24-a0a7-2f863e'
        post_data['password'] = '8a88432d-33db-4d24-a0a7-2f863e7e8e4a'

        user1 = User.objects.create_user(post_data['username'], None, post_data['password'])
        user1.save()

        worker = WorkerEntry.objects.create(
            name='worker-1',
            uuid=post_data['username'],
            description='One Worker :)',
            user=user1
        )

        resp = self.client.post(
            '/main/bluesteelworker/login/',
            data=json.dumps(post_data),
            content_type='text/plain'
        )

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual('Access granted!', resp_obj['message'])
        self.assertEqual(user1.id, int(self.client.session['_auth_user_id']))

    def test_login_worker_with_bad_password(self):
        post_data = {}
        post_data['username'] = 'bad-login'
        post_data['password'] = 'bad-password'

        user1 = User.objects.create_user(
            username='8a88432d-33db-4d24-a0a7-2f863e7e8e4a',
            email=None,
            password='8a88432d-33db-4d24-a0a7-2f863e7e8e4a'
        )
        user1.save()

        worker = WorkerEntry.objects.create(
            name='worker-1',
            uuid=post_data['username'],
            description='One Worker :)',
            user=user1
        )

        resp = self.client.post(
            '/main/bluesteelworker/login/',
            data=json.dumps(post_data),
            content_type='text/plain'
        )

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(401, resp_obj['status'])
        self.assertEqual('Access denied!', resp_obj['message'])
        self.assertEqual(False, self.client.session.has_key('_auth_user_id'))

    def test_update_activity(self):
        update_time_1 = WorkerEntry.objects.filter(id=self.worker_1.id).first().updated_at

        resp = self.client.post(
            '/main/bluesteelworker/{0}/update/activity/'.format(self.worker_1.id),
            data='',
            content_type='text/plain'
        )

        update_time_2 = WorkerEntry.objects.filter(id=self.worker_1.id).first().updated_at

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertFalse(update_time_1 == update_time_2)
        self.assertTrue(update_time_1 < update_time_2)

    def test_save_worker(self):
        worker_new = WorkerEntry.objects.create(
            name='worker-new',
            uuid='8a88432d-33db-4d24-a0a7-2f863e111111',
            description='description-1',
            git_feeder=False,
            user=self.user1
        )

        self.assertEqual('description-1', worker_new.description)
        self.assertFalse(worker_new.git_feeder)

        post_data = {}
        post_data['description'] = 'description-2'
        post_data['git_feeder'] = True
        post_data['max_feed_reports'] = 30

        resp = self.client.post(
            '/main/bluesteelworker/{0}/save/'.format(worker_new.id),
            data=json.dumps(post_data),
            content_type='text/plain'
        )

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        worker = WorkerEntry.objects.filter(id=worker_new.id).first()

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual('description-2', worker.description)
        self.assertEqual(True, worker.git_feeder)
        self.assertEqual(30, worker.max_feed_reports)


    def test_get_worker_files_hash_exists(self):
        WorkerFilesHashEntry.objects.create(files_hash='aaaa')

        resp = self.client.get('/main/bluesteelworker/hash/')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual('aaaa', resp_obj['data']['worker_files_hash'])

    def test_get_worker_files_hash_does_not_exists(self):
        resp = self.client.get('/main/bluesteelworker/hash/')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(400, resp_obj['status'])
        self.assertEqual('Worker files hash not found', resp_obj['message'])
