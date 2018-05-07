""" Git Feed Views commit tests """

from django.test import TestCase
from django.test import Client
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from app.logic.gitrepo.models.GitProjectModel import GitProjectEntry
from app.logic.gitrepo.models.GitUserModel import GitUserEntry
from app.logic.gitrepo.models.GitCommitModel import GitCommitEntry
from app.logic.gitrepo.models.GitParentModel import GitParentEntry
from app.logic.gitrepo.models.GitDiffModel import GitDiffEntry
from app.logic.gitrepo.models.GitBranchModel import GitBranchEntry
from app.logic.gitrepo.models.GitBranchTrailModel import GitBranchTrailEntry
from app.logic.gitfeeder.helper import FeederTestHelper
from app.logic.gitfeeder.models.FeedModel import FeedEntry
from app.logic.commandrepo.models.CommandGroupModel import CommandGroupEntry
from app.logic.commandrepo.models.CommandSetModel import CommandSetEntry
from app.logic.commandrepo.models.CommandModel import CommandEntry
from app.logic.commandrepo.models.CommandResultModel import CommandResultEntry
from app.logic.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.logic.benchmark.models.BenchmarkExecutionModel import BenchmarkExecutionEntry
from app.logic.benchmark.models.BenchmarkFluctuationWaiverModel import BenchmarkFluctuationWaiverEntry
from app.logic.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.logic.bluesteelworker.models.WorkerModel import WorkerEntry
from app.logic.mailing.models.StackedMailModel import StackedMailEntry
from app.logic.httpcommon import res
from datetime import timedelta
import json
import os
import hashlib
import shutil

class GitFeedViewsCommitTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user('user1@test.com', 'user1@test.com', 'pass1')
        self.user1.save()
        self.user2 = User.objects.create_user('user2@test.com', 'user2@test.com', 'pass2')
        self.user2.save()
        self.git_project1 = GitProjectEntry.objects.create(url='http://test/')
        self.git_user1 = GitUserEntry.objects.create(
            project=self.git_project1,
            name='user1',
            email='user1@test.com'
        )


    def tearDown(self):
        pass

    def test_feed_simple_commit(self):
        commit_time = str(timezone.now().isoformat())
        commit1 = FeederTestHelper.create_commit(1, [], 'user1', 'user1@test.com', commit_time, commit_time)

        branch1 = FeederTestHelper.create_branch('master', 1, 'master', 1, 1, [1], 'merge-target-content')

        feed_data = {}
        feed_data['commits'] = []
        feed_data['commits'].append(commit1)
        feed_data['branches'] = []
        feed_data['branches'].append(branch1)

        post_data = FeederTestHelper.create_feed_data(feed_data)

        resp = self.client.post(
            '/main/feed/commit/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(post_data),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual(1, GitCommitEntry.objects.all().count())
        self.assertEqual(1, GitBranchEntry.objects.all().count())

        branch_entry = GitBranchEntry.objects.all().first()
        self.assertEqual('0000100001000010000100001000010000100001', branch_entry.commit.commit_hash)
        self.assertEqual('master', branch_entry.name)

    def test_feed_reports_have_correct_user_assign(self):
        post_data = {}
        post_data['reports'] = FeederTestHelper.get_default_report(1)

        self.client.login(username='user1@test.com', password='pass1')
        resp = self.client.post(
            '/main/feed/report/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(post_data),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual(1, CommandGroupEntry.objects.filter(user=self.user1).count())


    def test_feed_simple_commit_already_present(self):
        git_commit1 = GitCommitEntry.objects.create(
            project=self.git_project1,
            commit_hash='0000100001000010000100001000010000100001',
            author=self.git_user1,
            author_date=timezone.now(),
            committer=self.git_user1,
            committer_date=timezone.now()
        )

        commit_time = str(timezone.now().isoformat())
        commit1 = FeederTestHelper.create_commit(1, [], 'user1', 'user1@test.com', commit_time, commit_time)

        branch1 = FeederTestHelper.create_branch('master', 1, 'master', 1, 1, [1], 'merge-target-content')

        feed_data = {}
        feed_data['commits'] = []
        feed_data['commits'].append(commit1)
        feed_data['branches'] = []
        feed_data['branches'].append(branch1)

        post_data = FeederTestHelper.create_feed_data(feed_data)

        resp = self.client.post(
            '/main/feed/commit/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(post_data),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual(1, GitCommitEntry.objects.all().count())
        self.assertEqual(1, GitBranchEntry.objects.all().count())

        branch_entry = GitBranchEntry.objects.all().first()
        self.assertEqual('0000100001000010000100001000010000100001', branch_entry.commit.commit_hash)
        self.assertEqual('master', branch_entry.name)


    def test_feed_fail_because_commits_are_not_unique(self):
        commit_time = str(timezone.now().isoformat())
        commit1 = FeederTestHelper.create_commit(1, [], 'user1', 'user1@test.com', commit_time, commit_time)
        commit2 = FeederTestHelper.create_commit(1, [], 'user1', 'user1@test.com', commit_time, commit_time)
        commit3 = FeederTestHelper.create_commit(2, [], 'user1', 'user1@test.com', commit_time, commit_time)
        commit4 = FeederTestHelper.create_commit(3, [], 'user1', 'user1@test.com', commit_time, commit_time)

        branch1 = FeederTestHelper.create_branch('master', 3, 'master', 3, 1, [3, 1], 'merge-target-content')

        feed_data = {}
        feed_data['commits'] = []
        feed_data['commits'].append(commit1)
        feed_data['commits'].append(commit2)
        feed_data['commits'].append(commit3)
        feed_data['commits'].append(commit4)
        feed_data['branches'] = []
        feed_data['branches'].append(branch1)

        post_data = FeederTestHelper.create_feed_data(feed_data)

        resp = self.client.post(
            '/main/feed/commit/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(post_data),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(400, resp_obj['status'])
        self.assertEqual('Commits not correct', resp_obj['message'])
        self.assertEqual(0, GitCommitEntry.objects.all().count())
        self.assertEqual(0, GitBranchEntry.objects.all().count())


    def test_two_commits_one_parent(self):
        commit_time = str(timezone.now().isoformat())
        commit1 = FeederTestHelper.create_commit(1, [], 'user1', 'user1@test.com', commit_time, commit_time)
        commit2 = FeederTestHelper.create_commit(2, [], 'user1', 'user1@test.com', commit_time, commit_time)

        commit1['parent_hashes'].append(commit2['hash'])

        branch1 = FeederTestHelper.create_branch('master', 1, 'master', 1, 1, [1], 'merge-target-content')

        feed_data = {}
        feed_data['commits'] = []
        feed_data['commits'].append(commit1)
        feed_data['commits'].append(commit2)
        feed_data['branches'] = []
        feed_data['branches'].append(branch1)

        post_data = FeederTestHelper.create_feed_data(feed_data)

        resp = self.client.post(
            '/main/feed/commit/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(post_data),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual(2, GitCommitEntry.objects.all().count())
        self.assertEqual(1, GitParentEntry.objects.all().count())
        self.assertEqual(1, GitBranchEntry.objects.all().count())

        parent_entry = GitParentEntry.objects.all().first()
        self.assertEqual('0000200002000020000200002000020000200002', parent_entry.parent.commit_hash)
        self.assertEqual('0000100001000010000100001000010000100001', parent_entry.son.commit_hash)

        branch_entry = GitBranchEntry.objects.all().first()
        self.assertEqual('0000100001000010000100001000010000100001', branch_entry.commit.commit_hash)
        self.assertEqual('master', branch_entry.name)


    def test_feed_fails_because_bad_constructed_parent(self):
        commit_time = str(timezone.now().isoformat())
        commit1 = FeederTestHelper.create_commit(1, [], 'user1', 'user1@test.com', commit_time, commit_time)
        commit2 = FeederTestHelper.create_commit(2, [3], 'user1', 'user1@test.com', commit_time, commit_time)

        branch1 = FeederTestHelper.create_branch('master', 2, 'master', 2, 1, [2, 1], 'merge-target-content')

        feed_data = {}
        feed_data['commits'] = []
        feed_data['commits'].append(commit1)
        feed_data['commits'].append(commit2)
        feed_data['branches'] = []
        feed_data['branches'].append(branch1)

        post_data = FeederTestHelper.create_feed_data(feed_data)

        resp = self.client.post(
            '/main/feed/commit/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(post_data),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(400, resp_obj['status'])
        self.assertEqual('Parents not correct', resp_obj['message'])

    def test_feed_only_care_about_the_first_parent_of_every_commit(self):
        commit_time = str(timezone.now().isoformat())
        commit1 = FeederTestHelper.create_commit(1, [], 'user1', 'user1@test.com', commit_time, commit_time)
        commit2 = FeederTestHelper.create_commit(2, [1, 3], 'user1', 'user1@test.com', commit_time, commit_time)

        branch1 = FeederTestHelper.create_branch('master', 2, 'master', 2, 1, [2, 1], 'merge-target-content')

        feed_data = {}
        feed_data['commits'] = []
        feed_data['commits'].append(commit1)
        feed_data['commits'].append(commit2)
        feed_data['branches'] = []
        feed_data['branches'].append(branch1)

        post_data = FeederTestHelper.create_feed_data(feed_data)

        resp = self.client.post(
            '/main/feed/commit/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(post_data),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual('Commits added correctly', resp_obj['message'])


    def test_feed_two_times(self):
        commit_time = str(timezone.now().isoformat())
        commit1 = FeederTestHelper.create_commit(1, [], 'user1', 'user1@test.com', commit_time, commit_time)
        commit2 = FeederTestHelper.create_commit(2, [1], 'user1', 'user1@test.com', commit_time, commit_time)
        commit3 = FeederTestHelper.create_commit(3, [1], 'user1', 'user1@test.com', commit_time, commit_time)

        branch1 = FeederTestHelper.create_branch('master', 2, 'master', 2, 1, [2, 1], 'merge-target-content')
        branch2 = FeederTestHelper.create_branch('branch-1', 3, 'master', 2, 1, [3, 1], 'merge-target-content-2')

        feed_data = {}
        feed_data['commits'] = []
        feed_data['commits'].append(commit1)
        feed_data['commits'].append(commit2)
        feed_data['commits'].append(commit3)
        feed_data['branches'] = []
        feed_data['branches'].append(branch1)
        feed_data['branches'].append(branch2)

        post_data = FeederTestHelper.create_feed_data(feed_data)

        resp = self.client.post(
            '/main/feed/commit/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(post_data),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)
        self.assertEqual(200, resp_obj['status'])

        commit4 = FeederTestHelper.create_commit(4, [2], 'user1', 'user1@test.com', commit_time, commit_time)
        commit5 = FeederTestHelper.create_commit(5, [3], 'user1', 'user1@test.com', commit_time, commit_time)

        branch1 = FeederTestHelper.create_branch('master', 4, 'master', 4, 1, [4, 2, 1], 'merge-target-content-3')
        branch2 = FeederTestHelper.create_branch('branch-1', 5, 'master', 4, 1, [5, 3, 1], 'merge-target-content-4')

        feed_data = {}
        feed_data['commits'] = []
        feed_data['commits'].append(commit4)
        feed_data['commits'].append(commit5)
        feed_data['branches'] = []
        feed_data['branches'].append(branch1)
        feed_data['branches'].append(branch2)

        post_data = FeederTestHelper.create_feed_data(feed_data)

        resp = self.client.post(
            '/main/feed/commit/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(post_data),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)
        self.assertEqual(200, resp_obj['status'])

        self.assertEqual(5, GitCommitEntry.objects.all().count())
        self.assertEqual(4, GitParentEntry.objects.all().count())
        self.assertEqual(2, GitBranchEntry.objects.all().count())
        self.assertEqual(6, GitBranchTrailEntry.objects.all().count())

        self.assertIsNotNone(GitCommitEntry.objects.filter(commit_hash='0000100001000010000100001000010000100001').first())
        self.assertIsNotNone(GitCommitEntry.objects.filter(commit_hash='0000200002000020000200002000020000200002').first())
        self.assertIsNotNone(GitCommitEntry.objects.filter(commit_hash='0000300003000030000300003000030000300003').first())
        self.assertIsNotNone(GitCommitEntry.objects.filter(commit_hash='0000400004000040000400004000040000400004').first())
        self.assertIsNotNone(GitCommitEntry.objects.filter(commit_hash='0000500005000050000500005000050000500005').first())

        self.assertIsNotNone(GitParentEntry.objects.filter(parent__commit_hash='0000100001000010000100001000010000100001', son__commit_hash='0000200002000020000200002000020000200002').first())
        self.assertIsNotNone(GitParentEntry.objects.filter(parent__commit_hash='0000100001000010000100001000010000100001', son__commit_hash='0000300003000030000300003000030000300003').first())
        self.assertIsNotNone(GitParentEntry.objects.filter(parent__commit_hash='0000200002000020000200002000020000200002', son__commit_hash='0000400004000040000400004000040000400004').first())
        self.assertIsNotNone(GitParentEntry.objects.filter(parent__commit_hash='0000300003000030000300003000030000300003', son__commit_hash='0000500005000050000500005000050000500005').first())

        self.assertIsNotNone(GitBranchEntry.objects.filter(name='master').first())
        self.assertIsNotNone(GitBranchEntry.objects.filter(name='branch-1').first())

        self.assertIsNotNone(GitBranchTrailEntry.objects.filter(commit__commit_hash='0000100001000010000100001000010000100001', branch__name='master').first())
        self.assertIsNotNone(GitBranchTrailEntry.objects.filter(commit__commit_hash='0000200002000020000200002000020000200002', branch__name='master').first())
        self.assertIsNotNone(GitBranchTrailEntry.objects.filter(commit__commit_hash='0000400004000040000400004000040000400004', branch__name='master').first())
        self.assertIsNotNone(GitBranchTrailEntry.objects.filter(commit__commit_hash='0000100001000010000100001000010000100001', branch__name='branch-1').first())
        self.assertIsNotNone(GitBranchTrailEntry.objects.filter(commit__commit_hash='0000300003000030000300003000030000300003', branch__name='branch-1').first())
        self.assertIsNotNone(GitBranchTrailEntry.objects.filter(commit__commit_hash='0000500005000050000500005000050000500005', branch__name='branch-1').first())

    def test_feed_two_times_populate_fluctuation_waivers(self):
        commit_time = str(timezone.now().isoformat())
        commit1 = FeederTestHelper.create_commit(1, [], 'user1', 'user1@test.com', commit_time, commit_time)
        commit2 = FeederTestHelper.create_commit(2, [1], 'user1', 'user1@test.com', commit_time, commit_time)
        commit3 = FeederTestHelper.create_commit(3, [1], 'user2', 'user2@test.com', commit_time, commit_time)

        branch1 = FeederTestHelper.create_branch('master', 2, 'master', 2, 1, [2, 1], 'merge-target-content')
        branch2 = FeederTestHelper.create_branch('branch-1', 3, 'master', 2, 1, [3, 1], 'merge-target-content-2')

        feed_data = {}
        feed_data['commits'] = []
        feed_data['commits'].append(commit1)
        feed_data['commits'].append(commit2)
        feed_data['commits'].append(commit3)
        feed_data['branches'] = []
        feed_data['branches'].append(branch1)
        feed_data['branches'].append(branch2)

        post_data = FeederTestHelper.create_feed_data(feed_data)

        resp = self.client.post(
            '/main/feed/commit/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(post_data),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual(2, BenchmarkFluctuationWaiverEntry.objects.all().count())
        self.assertEqual(1, BenchmarkFluctuationWaiverEntry.objects.filter(git_user__name='user1').count())
        self.assertEqual(1, BenchmarkFluctuationWaiverEntry.objects.filter(git_user__name='user2').count())

        commit4 = FeederTestHelper.create_commit(4, [2], 'user1', 'user1@test.com', commit_time, commit_time)
        commit5 = FeederTestHelper.create_commit(5, [3], 'user3', 'user3@test.com', commit_time, commit_time)

        branch1 = FeederTestHelper.create_branch('master', 4, 'master', 4, 1, [4, 2, 1], 'merge-target-content-3')
        branch2 = FeederTestHelper.create_branch('branch-1', 5, 'master', 4, 1, [5, 3, 1], 'merge-target-content-4')

        feed_data = {}
        feed_data['commits'] = []
        feed_data['commits'].append(commit4)
        feed_data['commits'].append(commit5)
        feed_data['branches'] = []
        feed_data['branches'].append(branch1)
        feed_data['branches'].append(branch2)

        post_data = FeederTestHelper.create_feed_data(feed_data)

        resp = self.client.post(
            '/main/feed/commit/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(post_data),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual(3, BenchmarkFluctuationWaiverEntry.objects.all().count())
        self.assertEqual(1, BenchmarkFluctuationWaiverEntry.objects.filter(git_user__name='user1').count())
        self.assertEqual(1, BenchmarkFluctuationWaiverEntry.objects.filter(git_user__name='user2').count())
        self.assertEqual(1, BenchmarkFluctuationWaiverEntry.objects.filter(git_user__name='user3').count())


    def test_feed_commit_create_benchmark_execution_because_benchmark_definition(self):
        command_group = CommandGroupEntry.objects.create()
        command_set = CommandSetEntry.objects.create(
            group=command_group
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

        worker1 = WorkerEntry.objects.create(
            name='worker-name-1',
            uuid='uuid-worker-1',
            operative_system='osx',
            description='long-description-1',
            user=self.user1,
            git_feeder=False
        )

        worker2 = WorkerEntry.objects.create(
            name='worker-name-2',
            uuid='uuid-worker-2',
            operative_system='osx',
            description='long-description-2',
            user=self.user2,
            git_feeder=False
        )

        commit_time = str(timezone.now().isoformat())
        commit1 = FeederTestHelper.create_commit(1, [], 'user1', 'user1@test.com', commit_time, commit_time)

        branch1 = FeederTestHelper.create_branch('master', 1, 'master', 1, 1, [1], 'merge-target-content')

        feed_data = {}
        feed_data['commits'] = []
        feed_data['commits'].append(commit1)
        feed_data['branches'] = []
        feed_data['branches'].append(branch1)

        post_data = FeederTestHelper.create_feed_data(feed_data)

        self.assertEqual(0, BenchmarkExecutionEntry.objects.all().count())

        resp = self.client.post(
            '/main/feed/commit/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(post_data),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual(1, GitCommitEntry.objects.all().count())
        self.assertEqual(1, GitBranchEntry.objects.all().count())

        branch_entry = GitBranchEntry.objects.all().first()
        self.assertEqual('0000100001000010000100001000010000100001', branch_entry.commit.commit_hash)
        self.assertEqual('master', branch_entry.name)
        self.assertEqual(4, BenchmarkExecutionEntry.objects.all().count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(commit__commit_hash='0000100001000010000100001000010000100001', worker=worker1, definition=benchmark_definition1).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(commit__commit_hash='0000100001000010000100001000010000100001', worker=worker1, definition=benchmark_definition2).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(commit__commit_hash='0000100001000010000100001000010000100001', worker=worker2, definition=benchmark_definition1).count())
        self.assertEqual(1, BenchmarkExecutionEntry.objects.filter(commit__commit_hash='0000100001000010000100001000010000100001', worker=worker2, definition=benchmark_definition2).count())


    def test_view_josn_purge_all_feed_reports_from_a_worker(self):
        git_project2 = GitProjectEntry.objects.create(url='http://test/2/')

        worker1 = WorkerEntry.objects.create(
            name='worker-name-1',
            uuid='uuid-worker-1',
            operative_system='osx',
            description='long-description-1',
            user=self.user1,
            git_feeder=False
        )

        command_group_1 = CommandGroupEntry.objects.create()
        command_group_2 = CommandGroupEntry.objects.create()
        command_group_3 = CommandGroupEntry.objects.create()
        command_group_4 = CommandGroupEntry.objects.create()

        feed_1_1 = FeedEntry.objects.create(command_group=command_group_1, git_project=self.git_project1, worker=worker1)
        feed_1_2 = FeedEntry.objects.create(command_group=command_group_2, git_project=self.git_project1, worker=worker1)
        feed_2_1 = FeedEntry.objects.create(command_group=command_group_3, git_project=git_project2, worker=worker1)
        feed_2_2 = FeedEntry.objects.create(command_group=command_group_4, git_project=git_project2, worker=worker1)

        self.assertEqual(4, FeedEntry.objects.all().count())
        self.assertEqual(1, CommandGroupEntry.objects.filter(id=command_group_1.id).count())
        self.assertEqual(1, CommandGroupEntry.objects.filter(id=command_group_2.id).count())
        self.assertEqual(1, CommandGroupEntry.objects.filter(id=command_group_3.id).count())
        self.assertEqual(1, CommandGroupEntry.objects.filter(id=command_group_4.id).count())

        resp = self.client.post(
            '/main/feed/report/worker/{0}/purge/all/'.format(worker1.id),
            data = '',
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])

        self.assertEqual(0, FeedEntry.objects.all().count())
        self.assertEqual(0, FeedEntry.objects.filter(git_project=self.git_project1, worker=worker1).count())
        self.assertEqual(0, FeedEntry.objects.filter(git_project=git_project2, worker=worker1).count())
        self.assertEqual(0, CommandGroupEntry.objects.filter(id=command_group_1.id).count())
        self.assertEqual(0, CommandGroupEntry.objects.filter(id=command_group_2.id).count())
        self.assertEqual(0, CommandGroupEntry.objects.filter(id=command_group_3.id).count())
        self.assertEqual(0, CommandGroupEntry.objects.filter(id=command_group_4.id).count())


    def test_view_purge_old_feed_reports_from_a_worker(self):
        git_project2 = GitProjectEntry.objects.create(url='http://test/2/')

        worker1 = WorkerEntry.objects.create(
            name='worker-name-1',
            uuid='uuid-worker-1',
            operative_system='osx',
            description='long-description-1',
            user=self.user1,
            git_feeder=False
        )

        command_group_1 = CommandGroupEntry.objects.create()
        command_group_2 = CommandGroupEntry.objects.create()
        command_group_3 = CommandGroupEntry.objects.create()
        command_group_4 = CommandGroupEntry.objects.create()

        feed_1_1 = FeedEntry.objects.create(command_group=command_group_1, git_project=self.git_project1, worker=worker1)
        feed_1_2 = FeedEntry.objects.create(command_group=command_group_2, git_project=self.git_project1, worker=worker1)
        feed_2_1 = FeedEntry.objects.create(command_group=command_group_3, git_project=git_project2, worker=worker1)
        feed_2_2 = FeedEntry.objects.create(command_group=command_group_4, git_project=git_project2, worker=worker1)

        self.assertEqual(4, FeedEntry.objects.all().count())
        self.assertEqual(1, CommandGroupEntry.objects.filter(id=command_group_1.id).count())
        self.assertEqual(1, CommandGroupEntry.objects.filter(id=command_group_2.id).count())
        self.assertEqual(1, CommandGroupEntry.objects.filter(id=command_group_3.id).count())
        self.assertEqual(1, CommandGroupEntry.objects.filter(id=command_group_4.id).count())

        resp = self.client.post(
            '/main/feed/report/worker/{0}/purge/keep/2/'.format(worker1.id),
            data = '',
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])

        self.assertEqual(2, FeedEntry.objects.all().count())
        self.assertEqual(0, FeedEntry.objects.filter(git_project=self.git_project1, worker=worker1).count())
        self.assertEqual(2, FeedEntry.objects.filter(git_project=git_project2, worker=worker1).count())
        self.assertEqual(0, CommandGroupEntry.objects.filter(id=command_group_1.id).count())
        self.assertEqual(0, CommandGroupEntry.objects.filter(id=command_group_2.id).count())
        self.assertEqual(1, CommandGroupEntry.objects.filter(id=command_group_3.id).count())
        self.assertEqual(1, CommandGroupEntry.objects.filter(id=command_group_4.id).count())


    def test_view_send_notifications_on_fluctuation_greater_than_45_percent(self):
        BenchmarkFluctuationWaiverEntry.objects.create(git_user=self.git_user1, notification_allowed=True);
        worker1 = WorkerEntry.objects.create(name='worker-name-1', uuid='uuid-worker-1', operative_system='osx', description='long-description-1', user=self.user1, git_feeder=False)

        command_group = CommandGroupEntry.objects.create()
        command_set = CommandSetEntry.objects.create(group=command_group)

        bluesteel_layout = BluesteelLayoutEntry.objects.create(name='Layout', active=True, project_index_path=0)
        bluesteel_project = BluesteelProjectEntry.objects.create(name='Project', order=0, layout=bluesteel_layout, command_group=command_group, git_project=self.git_project1)
        benchmark_definition1 = BenchmarkDefinitionEntry.objects.create(name='BenchmarkDefinition1', layout=bluesteel_layout, project=bluesteel_project, command_set=command_set, revision=28)
        benchmark_definition1.max_fluctuation_percent = 45
        benchmark_definition1.save()

        commit0 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000000000000000000000000000000000000000', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())
        commit1 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000100001000010000100001000010000100001', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())

        branch_test = GitBranchEntry.objects.create(project=self.git_project1, name='branch-test', commit=commit1)

        trail0 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch_test, commit=commit0, order=5)
        trail1 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch_test, commit=commit1, order=4)

        parent0_1 = GitParentEntry.objects.create(project=self.git_project1, parent=commit0, son=commit1, order=0)

        report0 = CommandSetEntry.objects.create(group=None)
        report1 = CommandSetEntry.objects.create(group=None)

        com0 = CommandEntry.objects.create(command_set=report0, command='command0', order=0)
        out0 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1.0, 1.0, 1.0, 1.0, 1.0]}])
        CommandResultEntry.objects.create(command=com0, out=out0, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())

        benchmark_execution0 = BenchmarkExecutionEntry.objects.create(definition=benchmark_definition1, commit=commit0, worker=worker1, report=report0, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)
        benchmark_execution1 = BenchmarkExecutionEntry.objects.create(definition=benchmark_definition1, commit=commit1, worker=worker1, report=report1, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)

        self.assertEqual(0, StackedMailEntry.objects.all().count())

        com_data = {}
        com_data['command'] = 'command-1'
        com_data['result'] = {}
        com_data['result']['status'] = 0
        com_data['result']['out'] = [{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [2.0, 2.0, 2.0, 2.0, 2.0]}]
        com_data['result']['error'] = ''
        com_data['result']['start_time'] = str(timezone.now())
        com_data['result']['finish_time'] = str(timezone.now())

        bench_data = {}
        bench_data['command_set'] = []
        bench_data['command_set'].append(com_data)

        resp = self.client.post(
            '/main/execution/{0}/save/'.format(benchmark_execution1.id),
            data = json.dumps(bench_data),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual(1, StackedMailEntry.objects.all().count())

        self.assertEqual(1, StackedMailEntry.objects.all().count())
        email = StackedMailEntry.objects.all().first()

        self.assertTrue('Commit Hash: 0000100001000010000100001000010000100001' in email.content)
        self.assertTrue('Commit Author: user1' in email.content)
        self.assertTrue('Commit Author Email: user1@test.com' in email.content)
        self.assertTrue('Worker Name: worker-name-1' in email.content)
        self.assertTrue('Worker Operative System: osx' in email.content)
        self.assertTrue('Benchmark Definition Name: BenchmarkDefinition1' in email.content)
        self.assertTrue('Parent commit: 0000000' in email.content)
        self.assertTrue('Parent median result: 1.0' in email.content)
        self.assertTrue('Parent fluctuation vs Current commit: -50.0%' in email.content)
        self.assertTrue('Current commit: 0000100' in email.content)
        self.assertTrue('Current median result: 2.0' in email.content)
        self.assertTrue('http://testserver/main/execution/2/window/' in email.content)


    def test_view_not_sending_notifications_because_fluctuation_not_enough(self):
        BenchmarkFluctuationWaiverEntry.objects.create(git_user=self.git_user1, notification_allowed=True);
        worker1 = WorkerEntry.objects.create(name='worker-name-1', uuid='uuid-worker-1', operative_system='osx', description='long-description-1', user=self.user1, git_feeder=False)

        command_group = CommandGroupEntry.objects.create()
        command_set = CommandSetEntry.objects.create(group=command_group)

        bluesteel_layout = BluesteelLayoutEntry.objects.create(name='Layout', active=True, project_index_path=0)
        bluesteel_project = BluesteelProjectEntry.objects.create(name='Project', order=0, layout=bluesteel_layout, command_group=command_group, git_project=self.git_project1)
        benchmark_definition1 = BenchmarkDefinitionEntry.objects.create(name='BenchmarkDefinition1', layout=bluesteel_layout, project=bluesteel_project, command_set=command_set, revision=28)
        benchmark_definition1.max_fluctuation_percent = 15
        benchmark_definition1.save()

        commit0 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000000000000000000000000000000000000000', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())
        commit1 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash='0000100001000010000100001000010000100001', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())

        branch_test = GitBranchEntry.objects.create(project=self.git_project1, name='branch-test', commit=commit1)

        trail0 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch_test, commit=commit0, order=5)
        trail1 = GitBranchTrailEntry.objects.create(project=self.git_project1, branch=branch_test, commit=commit1, order=4)

        parent0_1 = GitParentEntry.objects.create(project=self.git_project1, parent=commit0, son=commit1, order=0)

        report0 = CommandSetEntry.objects.create(group=None)
        report1 = CommandSetEntry.objects.create(group=None)

        com0 = CommandEntry.objects.create(command_set=report0, command='command0', order=0)
        out0 = json.dumps([{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1.0, 1.0, 1.0, 1.0, 1.0]}])
        CommandResultEntry.objects.create(command=com0, out=out0, error='no error', status=0, start_time=timezone.now(), finish_time=timezone.now())

        benchmark_execution0 = BenchmarkExecutionEntry.objects.create(definition=benchmark_definition1, commit=commit0, worker=worker1, report=report0, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)
        benchmark_execution1 = BenchmarkExecutionEntry.objects.create(definition=benchmark_definition1, commit=commit1, worker=worker1, report=report1, invalidated=False, revision_target=28, status=BenchmarkExecutionEntry.READY)

        self.assertEqual(0, StackedMailEntry.objects.all().count())

        com_data = {}
        com_data['command'] = 'command-1'
        com_data['result'] = {}
        com_data['result']['status'] = 0
        com_data['result']['out'] = [{'visual_type' : 'vertical_bars', 'id' : 'id1', 'data' : [1.1, 1.1, 1.1, 1.1, 1.1]}]
        com_data['result']['error'] = ''
        com_data['result']['start_time'] = str(timezone.now())
        com_data['result']['finish_time'] = str(timezone.now())

        bench_data = {}
        bench_data['command_set'] = []
        bench_data['command_set'].append(com_data)

        resp = self.client.post(
            '/main/execution/{0}/save/'.format(benchmark_execution1.id),
            data = json.dumps(bench_data),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual(0, StackedMailEntry.objects.all().count())



    def test_view_purge_when_feeding_reports(self):
        git_project2 = GitProjectEntry.objects.create(url='http://test/2/')

        worker1 = WorkerEntry.objects.create(
            name='worker-name-1',
            uuid='uuid-worker-1',
            operative_system='osx',
            description='long-description-1',
            user=self.user1,
            git_feeder=False,
            max_feed_reports=3,
        )

        command_group_1 = CommandGroupEntry.objects.create()
        command_group_2 = CommandGroupEntry.objects.create()
        command_group_3 = CommandGroupEntry.objects.create()
        command_group_4 = CommandGroupEntry.objects.create()
        command_group_5 = CommandGroupEntry.objects.create()

        feed_1_1 = FeedEntry.objects.create(command_group=command_group_1, git_project=self.git_project1, worker=worker1)
        feed_1_2 = FeedEntry.objects.create(command_group=command_group_2, git_project=self.git_project1, worker=worker1)
        feed_2_1 = FeedEntry.objects.create(command_group=command_group_3, git_project=git_project2, worker=worker1)
        feed_2_2 = FeedEntry.objects.create(command_group=command_group_4, git_project=git_project2, worker=worker1)
        feed_2_2 = FeedEntry.objects.create(command_group=command_group_5, git_project=git_project2, worker=worker1)

        self.assertEqual(5, FeedEntry.objects.all().count())
        self.assertEqual(1, CommandGroupEntry.objects.filter(id=command_group_1.id).count())
        self.assertEqual(1, CommandGroupEntry.objects.filter(id=command_group_2.id).count())
        self.assertEqual(1, CommandGroupEntry.objects.filter(id=command_group_3.id).count())
        self.assertEqual(1, CommandGroupEntry.objects.filter(id=command_group_4.id).count())
        self.assertEqual(1, CommandGroupEntry.objects.filter(id=command_group_5.id).count())

        post_data = {}
        post_data['reports'] = FeederTestHelper.get_default_report(1)

        self.client.login(username='user1@test.com', password='pass1')
        resp = self.client.post(
            '/main/feed/report/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(post_data),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])

        self.assertEqual(3, FeedEntry.objects.all().count())
        self.assertEqual(1, FeedEntry.objects.filter(git_project=self.git_project1, worker=worker1).count())
        self.assertEqual(2, FeedEntry.objects.filter(git_project=git_project2, worker=worker1).count())
        self.assertEqual(0, CommandGroupEntry.objects.filter(id=command_group_1.id).count())
        self.assertEqual(0, CommandGroupEntry.objects.filter(id=command_group_2.id).count())
        self.assertEqual(0, CommandGroupEntry.objects.filter(id=command_group_3.id).count())
        self.assertEqual(1, CommandGroupEntry.objects.filter(id=command_group_4.id).count())
        self.assertEqual(1, CommandGroupEntry.objects.filter(id=command_group_5.id).count())
