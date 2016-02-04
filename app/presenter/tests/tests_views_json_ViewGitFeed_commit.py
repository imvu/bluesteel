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
from app.logic.commandrepo.models.CommandGroupModel import CommandGroupEntry
from app.logic.commandrepo.models.CommandSetModel import CommandSetEntry
from app.logic.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.logic.benchmark.models.BenchmarkExecutionModel import BenchmarkExecutionEntry
from app.logic.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.logic.bluesteelworker.models.WorkerModel import WorkerEntry
from app.logic.httpcommon import res
from datetime import timedelta
import json
import os
import hashlib
import shutil

# Create your tests here.

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
        feed_data['diffs'] = []
        feed_data['diffs'].append(FeederTestHelper.create_diff(1, 1, 'diff-1'))

        post_data = FeederTestHelper.create_feed_data_and_report(
            feed_data,
            FeederTestHelper.get_default_report(1)
        )

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
        commit_time = str(timezone.now().isoformat())
        commit1 = FeederTestHelper.create_commit(1, [], 'user1', 'user1@test.com', commit_time, commit_time)

        branch1 = FeederTestHelper.create_branch('master', 1, 'master', 1, 1, [1], 'merge-target-content')

        feed_data = {}
        feed_data['commits'] = []
        feed_data['commits'].append(commit1)
        feed_data['branches'] = []
        feed_data['branches'].append(branch1)
        feed_data['diffs'] = []
        feed_data['diffs'].append(FeederTestHelper.create_diff(1, 1, 'diff-1'))

        post_data = FeederTestHelper.create_feed_data_and_report(
            feed_data,
            FeederTestHelper.get_default_report(1)
        )

        self.client.login(username='user1@test.com', password='pass1')
        resp = self.client.post(
            '/main/feed/commit/project/{0}/'.format(self.git_project1.id),
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
        feed_data['diffs'] = []
        feed_data['diffs'].append(FeederTestHelper.create_diff(1, 1, 'diff-1'))

        post_data = FeederTestHelper.create_feed_data_and_report(
            feed_data,
            FeederTestHelper.get_default_report(1)
        )

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
        feed_data['diffs'] = []
        feed_data['diffs'].append(FeederTestHelper.create_diff(1, 1, 'diff-1'))
        feed_data['diffs'].append(FeederTestHelper.create_diff(2, 1, 'diff-2-1'))
        feed_data['diffs'].append(FeederTestHelper.create_diff(3, 2, 'diff-3-2'))

        post_data = FeederTestHelper.create_feed_data_and_report(
            feed_data,
            FeederTestHelper.get_default_report(1)
        )

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
        feed_data['diffs'] = []
        feed_data['diffs'].append(FeederTestHelper.create_diff(1, 1, 'diff-1'))
        feed_data['diffs'].append(FeederTestHelper.create_diff(2, 1, 'diff-2-1'))

        post_data = FeederTestHelper.create_feed_data_and_report(
            feed_data,
            FeederTestHelper.get_default_report(1)
        )

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
        feed_data['diffs'] = []
        feed_data['diffs'].append(FeederTestHelper.create_diff(1, 1, 'diff-1'))
        feed_data['diffs'].append(FeederTestHelper.create_diff(2, 1, 'diff-2-1'))

        post_data = FeederTestHelper.create_feed_data_and_report(
            feed_data,
            FeederTestHelper.get_default_report(1)
        )

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
        feed_data['diffs'] = []
        feed_data['diffs'].append(FeederTestHelper.create_diff(1, 1, 'diff-1'))
        feed_data['diffs'].append(FeederTestHelper.create_diff(2, 1, 'diff-2-1'))

        post_data = FeederTestHelper.create_feed_data_and_report(
            feed_data,
            FeederTestHelper.get_default_report(1)
        )

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
        feed_data['diffs'] = []
        feed_data['diffs'].append(FeederTestHelper.create_diff(1, 1, 'diff-1'))
        feed_data['diffs'].append(FeederTestHelper.create_diff(2, 1, 'diff-2-1'))
        feed_data['diffs'].append(FeederTestHelper.create_diff(3, 2, 'diff-3-2'))

        post_data = FeederTestHelper.create_feed_data_and_report(
            feed_data,
            FeederTestHelper.get_default_report(1)
        )

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
        feed_data['diffs'] = []
        feed_data['diffs'].append(FeederTestHelper.create_diff(4, 3, 'diff-4-3'))
        feed_data['diffs'].append(FeederTestHelper.create_diff(5, 4, 'diff-5-4'))

        post_data = FeederTestHelper.create_feed_data_and_report(
            feed_data,
            FeederTestHelper.get_default_report(1)
        )

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
        feed_data['diffs'] = []
        feed_data['diffs'].append(FeederTestHelper.create_diff(1, 1, 'diff-1'))

        post_data = FeederTestHelper.create_feed_data_and_report(
            feed_data,
            FeederTestHelper.get_default_report(1)
        )

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
