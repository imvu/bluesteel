""" GitFeederController tests """

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User, AnonymousUser
from app.logic.gitfeeder.models.FeedModel import FeedEntry
from app.logic.gitfeeder.controllers.GitFeederController import GitFeederController
from app.logic.gitfeeder.helper import FeederTestHelper
from app.logic.gitrepo.models.GitProjectModel import GitProjectEntry
from app.logic.gitrepo.models.GitParentModel import GitParentEntry
from app.logic.gitrepo.models.GitUserModel import GitUserEntry
from app.logic.gitrepo.models.GitCommitModel import GitCommitEntry
from app.logic.gitrepo.models.GitBranchModel import GitBranchEntry
from app.logic.gitrepo.models.GitBranchTrailModel import GitBranchTrailEntry
from app.logic.gitrepo.models.GitDiffModel import GitDiffEntry
from app.logic.bluesteelworker.models.WorkerModel import WorkerEntry

class GitFeederControllerTestCase(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user('user1@test.com', 'user1@test.com', 'pass1')
        self.user2 = User.objects.create_user('user2@test.com', 'user2@test.com', 'pass2')

        self.worker1 = WorkerEntry.objects.create(
            name='worker-name-1',
            uuid='uuid-worker-1',
            operative_system='osx',
            description='long-description-1',
            user=self.user1,
            git_feeder=False
        )


        self.time = str(timezone.now().isoformat())
        self.git_project1 = GitProjectEntry.objects.create(url='http://test/')
        self.git_user1 = GitUserEntry.objects.create(
            project=self.git_project1,
            name='user1',
            email='user1@test.com'
        )

    def tearDown(self):
        pass

    def test_get_commit_unique_set(self):
        commits = []
        commits.append(FeederTestHelper.create_commit(1, [], 'user1', 'user1@test.com', self.time, self.time))
        commits.append(FeederTestHelper.create_commit(2, [], 'user1', 'user1@test.com', self.time, self.time))
        commits.append(FeederTestHelper.create_commit(3, [], 'user1', 'user1@test.com', self.time, self.time))
        commits.append(FeederTestHelper.create_commit(4, [], 'user1', 'user1@test.com', self.time, self.time))
        commits.append(FeederTestHelper.create_commit(4, [], 'user1', 'user1@test.com', self.time, self.time))
        commits.append(FeederTestHelper.create_commit(4, [], 'user1', 'user1@test.com', self.time, self.time))

        res = GitFeederController.get_unique_commit_set(commits)

        commit_set = set()
        commit_set.add('0000100001000010000100001000010000100001')
        commit_set.add('0000200002000020000200002000020000200002')
        commit_set.add('0000300003000030000300003000030000300003')
        commit_set.add('0000400004000040000400004000040000400004')

        self.assertEqual(4, len(res))
        self.assertEqual(commit_set, res)

    def test_commits_are_unique(self):
        commits = []
        commits.append(FeederTestHelper.create_commit(1, [], 'user1', 'user1@test.com', self.time, self.time))
        commits.append(FeederTestHelper.create_commit(2, [], 'user1', 'user1@test.com', self.time, self.time))
        commits.append(FeederTestHelper.create_commit(3, [], 'user1', 'user1@test.com', self.time, self.time))
        commits.append(FeederTestHelper.create_commit(4, [], 'user1', 'user1@test.com', self.time, self.time))

        res = GitFeederController.are_commits_unique(commits)

        self.assertEqual(True, res[0])
        self.assertEqual(0, len(res[1]))

    def test_commits_are_not_unique(self):
        commits = []
        commits.append(FeederTestHelper.create_commit(1, [], 'user1', 'user1@test.com', self.time, self.time))
        commits.append(FeederTestHelper.create_commit(2, [], 'user1', 'user1@test.com', self.time, self.time))
        commits.append(FeederTestHelper.create_commit(2, [], 'user1', 'user1@test.com', self.time, self.time))
        commits.append(FeederTestHelper.create_commit(4, [], 'user1', 'user1@test.com', self.time, self.time))

        res = GitFeederController.are_commits_unique(commits)

        self.assertEqual(False, res[0])
        self.assertEqual(1, len(res[1]))
        self.assertEqual('Commit not unique 0000200002000020000200002000020000200002', res[1][0])

    def test_parents_are_correct(self):
        commits = []
        commits.append(FeederTestHelper.create_commit(1, [], 'user1', 'user1@test.com', self.time, self.time))
        commits.append(FeederTestHelper.create_commit(2, [1], 'user1', 'user1@test.com', self.time, self.time))
        commits.append(FeederTestHelper.create_commit(3, [1, 2], 'user1', 'user1@test.com', self.time, self.time))
        commits.append(FeederTestHelper.create_commit(4, [3], 'user1', 'user1@test.com', self.time, self.time))

        commit_set = GitFeederController.get_unique_commit_set(commits)

        res = GitFeederController.are_parent_hashes_correct(commits, commit_set, self.git_project1)

        self.assertEqual(True, res[0])
        self.assertEqual(0, len(res[1]))

    def test_parents_are_not_correct_because_hash_not_found_on_commits_list(self):
        commits = []
        commits.append(FeederTestHelper.create_commit(1, [], 'user1', 'user1@test.com', self.time, self.time))
        commits.append(FeederTestHelper.create_commit(2, [1], 'user1', 'user1@test.com', self.time, self.time))
        commits.append(FeederTestHelper.create_commit(3, [5, 2], 'user1', 'user1@test.com', self.time, self.time))
        commits.append(FeederTestHelper.create_commit(4, [3], 'user1', 'user1@test.com', self.time, self.time))

        commit_set = GitFeederController.get_unique_commit_set(commits)

        res = GitFeederController.are_parent_hashes_correct(commits, commit_set, self.git_project1)

        self.assertEqual(False, res[0])
        self.assertEqual(1, len(res[1]))
        self.assertEqual('Commit 0000300003000030000300003000030000300003 has parent hash 0000500005000050000500005000050000500005 but it is not present', res[1][0])


    def test_parents_are_correct_because_hash_found_on_previous_existing_commit(self):
        git_commit1 = GitCommitEntry.objects.create(
            project=self.git_project1,
            commit_hash='0000500005000050000500005000050000500005',
            author=self.git_user1,
            author_date=timezone.now(),
            committer=self.git_user1,
            committer_date=timezone.now()
        )

        commits = []
        commits.append(FeederTestHelper.create_commit(1, [], 'user1', 'user1@test.com', self.time, self.time))
        commits.append(FeederTestHelper.create_commit(2, [1], 'user1', 'user1@test.com', self.time, self.time))
        commits.append(FeederTestHelper.create_commit(3, [5, 2], 'user1', 'user1@test.com', self.time, self.time))
        commits.append(FeederTestHelper.create_commit(4, [3], 'user1', 'user1@test.com', self.time, self.time))

        commit_set = GitFeederController.get_unique_commit_set(commits)

        res = GitFeederController.are_parent_hashes_correct(commits, commit_set, self.git_project1)

        self.assertEqual(True, res[0])
        self.assertEqual(0, len(res[1]))

    def test_diffs_are_correct(self):
        commits = []
        commits.append(FeederTestHelper.create_commit(1, [],  'user1', 'user1@test.com', self.time, self.time))
        commits.append(FeederTestHelper.create_commit(2, [1], 'user1', 'user1@test.com', self.time, self.time))
        commits.append(FeederTestHelper.create_commit(3, [2], 'user1', 'user1@test.com', self.time, self.time))
        commits.append(FeederTestHelper.create_commit(4, [3], 'user1', 'user1@test.com', self.time, self.time))

        diffs = []
        diffs.append(FeederTestHelper.create_diff(1, 2, 'content-1'))
        diffs.append(FeederTestHelper.create_diff(2, 3, 'content-2'))
        diffs.append(FeederTestHelper.create_diff(3, 4, 'content-3'))

        commit_set = GitFeederController.get_unique_commit_set(commits)

        res = GitFeederController.are_diffs_correct(commit_set, diffs, self.git_project1)

        self.assertEqual(True, res[0])
        self.assertEqual(0, len(res[1]))

    def test_diffs_are_not_correct_because_commit_does_not_exists(self):
        commits = []
        commits.append(FeederTestHelper.create_commit(1, [],  'user1', 'user1@test.com', self.time, self.time))
        commits.append(FeederTestHelper.create_commit(2, [1], 'user1', 'user1@test.com', self.time, self.time))
        commits.append(FeederTestHelper.create_commit(3, [2], 'user1', 'user1@test.com', self.time, self.time))
        commits.append(FeederTestHelper.create_commit(4, [3], 'user1', 'user1@test.com', self.time, self.time))

        diffs = []
        diffs.append(FeederTestHelper.create_diff(1, 2, 'content-1'))
        diffs.append(FeederTestHelper.create_diff(2, 3, 'content-2'))
        diffs.append(FeederTestHelper.create_diff(4, 5, 'content-3'))

        commit_set = GitFeederController.get_unique_commit_set(commits)

        res = GitFeederController.are_diffs_correct(commit_set, diffs, self.git_project1)

        self.assertEqual(False, res[0])
        self.assertEqual(1, len(res[1]))
        self.assertEqual('Diff with a wrong parent commit 0000500005000050000500005000050000500005', res[1][0])

    def test_diffs_are_correct_because_previous_commit_already_exists(self):
        git_commit1 = GitCommitEntry.objects.create(
            project=self.git_project1,
            commit_hash='0000500005000050000500005000050000500005',
            author=self.git_user1,
            author_date=timezone.now(),
            committer=self.git_user1,
            committer_date=timezone.now()
        )

        commits = []
        commits.append(FeederTestHelper.create_commit(1, [],  'user1', 'user1@test.com', self.time, self.time))
        commits.append(FeederTestHelper.create_commit(2, [1], 'user1', 'user1@test.com', self.time, self.time))
        commits.append(FeederTestHelper.create_commit(3, [2], 'user1', 'user1@test.com', self.time, self.time))
        commits.append(FeederTestHelper.create_commit(4, [3], 'user1', 'user1@test.com', self.time, self.time))

        diffs = []
        diffs.append(FeederTestHelper.create_diff(1, 2, 'content-1'))
        diffs.append(FeederTestHelper.create_diff(2, 3, 'content-2'))
        diffs.append(FeederTestHelper.create_diff(4, 5, 'content-3'))

        commit_set = GitFeederController.get_unique_commit_set(commits)

        res = GitFeederController.are_diffs_correct(commit_set, diffs, self.git_project1)

        self.assertEqual(True, res[0])
        self.assertEqual(0, len(res[1]))

    def test_branch_are_correct(self):
        commits = []
        commits.append(FeederTestHelper.create_commit(1, [],  'user1', 'user1@test.com', self.time, self.time))
        commits.append(FeederTestHelper.create_commit(2, [1], 'user1', 'user1@test.com', self.time, self.time))
        commits.append(FeederTestHelper.create_commit(3, [2], 'user1', 'user1@test.com', self.time, self.time))
        commits.append(FeederTestHelper.create_commit(4, [3], 'user1', 'user1@test.com', self.time, self.time))

        trail = []
        trail.append(1)
        trail.append(2)
        trail.append(3)
        trail.append(4)

        branch_list = []
        branch_list.append(FeederTestHelper.create_branch('b1', 4, 'b2', 3, 2, trail, 'content'))

        commit_set = GitFeederController.get_unique_commit_set(commits)

        res = GitFeederController.are_branches_correct(commit_set, branch_list, self.git_project1)
        self.assertEqual(True, res[0])
        self.assertEqual(0, len(res[1]))

    def test_insert_branch_correctly(self):
        commit_time = str(timezone.now().isoformat())

        git_commit1 = GitCommitEntry.objects.create(
            project=self.git_project1,
            commit_hash=FeederTestHelper.hash_string(1),
            author=self.git_user1,
            author_date=commit_time,
            committer=self.git_user1,
            committer_date=commit_time
        )

        commit1 = FeederTestHelper.create_commit(1, [], 'user1', 'user1@test.com', commit_time, commit_time)
        branch1 = FeederTestHelper.create_branch('master', 1, 'master', 1, 1, [1], 'content')

        GitFeederController.insert_branches([branch1], self.git_project1)

        self.assertEqual(1, GitBranchEntry.objects.all().count())
        self.assertEqual('master', GitBranchEntry.objects.all().first().name)

        self.assertEqual(0, GitBranchTrailEntry.objects.all().count())

        self.assertEqual(1, GitCommitEntry.objects.all().count())
        self.assertEqual(FeederTestHelper.hash_string(1), GitCommitEntry.objects.all().first().commit_hash)


    def test_insert_branch_and_log_because_branch_commit_not_found(self):
        commit_time = str(timezone.now().isoformat())
        commit1 = FeederTestHelper.create_commit(1, [], 'user1', 'user1@test.com', commit_time, commit_time)

        branch1 = FeederTestHelper.create_branch('master', 1, 'master', 1, 1, [1], 'content')

        GitFeederController.insert_branches([branch1], self.git_project1)

        self.assertEqual(0, GitBranchTrailEntry.objects.all().count())
        self.assertEqual(0, GitCommitEntry.objects.all().count())
        self.assertEqual(0, GitBranchEntry.objects.all().count())


    def test_insert_parents_with_no_previous_parents_inserted(self):
        commit_time = str(timezone.now().isoformat())

        git_commit1 = GitCommitEntry.objects.create(
            project=self.git_project1,
            commit_hash=FeederTestHelper.hash_string(1),
            author=self.git_user1,
            author_date=commit_time,
            committer=self.git_user1,
            committer_date=commit_time
        )

        git_commit2 = GitCommitEntry.objects.create(
            project=self.git_project1,
            commit_hash=FeederTestHelper.hash_string(2),
            author=self.git_user1,
            author_date=commit_time,
            committer=self.git_user1,
            committer_date=commit_time
        )

        git_commit3 = GitCommitEntry.objects.create(
            project=self.git_project1,
            commit_hash=FeederTestHelper.hash_string(3),
            author=self.git_user1,
            author_date=commit_time,
            committer=self.git_user1,
            committer_date=commit_time
        )

        commit1 = FeederTestHelper.create_commit(1, [], 'user1', 'user1@test.com', commit_time, commit_time)
        commit2 = FeederTestHelper.create_commit(2, [1], 'user1', 'user1@test.com', commit_time, commit_time)
        commit3 = FeederTestHelper.create_commit(3, [2], 'user1', 'user1@test.com', commit_time, commit_time)

        commits = [commit1, commit2, commit3]

        GitFeederController.insert_parents(commits, self.git_project1)

        self.assertEqual(2, GitParentEntry.objects.all().count())
        self.assertEqual(1, GitParentEntry.objects.filter(parent__commit_hash=FeederTestHelper.hash_string(1), son__commit_hash=FeederTestHelper.hash_string(2)).count())
        self.assertEqual(1, GitParentEntry.objects.filter(parent__commit_hash=FeederTestHelper.hash_string(2), son__commit_hash=FeederTestHelper.hash_string(3)).count())


    def test_insert_parents_with_previous_parents_inserted(self):
        commit_time = str(timezone.now().isoformat())
        git_commit1 = GitCommitEntry.objects.create(
            project=self.git_project1,
            commit_hash=FeederTestHelper.hash_string(1),
            author=self.git_user1,
            author_date=commit_time,
            committer=self.git_user1,
            committer_date=commit_time
        )

        git_commit2 = GitCommitEntry.objects.create(
            project=self.git_project1,
            commit_hash=FeederTestHelper.hash_string(2),
            author=self.git_user1,
            author_date=commit_time,
            committer=self.git_user1,
            committer_date=commit_time
        )

        git_commit3 = GitCommitEntry.objects.create(
            project=self.git_project1,
            commit_hash=FeederTestHelper.hash_string(3),
            author=self.git_user1,
            author_date=commit_time,
            committer=self.git_user1,
            committer_date=commit_time
        )

        git_parent1 = GitParentEntry.objects.create(
            project=self.git_project1,
            parent=git_commit1,
            son=git_commit2,
            order=0
        )

        git_parent2 = GitParentEntry.objects.create(
            project=self.git_project1,
            parent=git_commit2,
            son=git_commit3,
            order=1
        )

        self.assertEqual(2, GitParentEntry.objects.all().count())
        self.assertEqual(1, GitParentEntry.objects.filter(parent__commit_hash=FeederTestHelper.hash_string(1), son__commit_hash=FeederTestHelper.hash_string(2)).count())
        self.assertEqual(1, GitParentEntry.objects.filter(parent__commit_hash=FeederTestHelper.hash_string(2), son__commit_hash=FeederTestHelper.hash_string(3)).count())

        commit1 = FeederTestHelper.create_commit(1, [], 'user1', 'user1@test.com', commit_time, commit_time)
        commit2 = FeederTestHelper.create_commit(2, [1], 'user1', 'user1@test.com', commit_time, commit_time)
        commit3 = FeederTestHelper.create_commit(3, [2], 'user1', 'user1@test.com', commit_time, commit_time)

        commits = [commit1, commit2, commit3]

        GitFeederController.insert_parents(commits, self.git_project1)

        self.assertEqual(2, GitParentEntry.objects.all().count())
        self.assertEqual(1, GitParentEntry.objects.filter(parent__commit_hash=FeederTestHelper.hash_string(1), son__commit_hash=FeederTestHelper.hash_string(2)).count())
        self.assertEqual(1, GitParentEntry.objects.filter(parent__commit_hash=FeederTestHelper.hash_string(2), son__commit_hash=FeederTestHelper.hash_string(3)).count())

    def test_insert_parents_with_no_commits_present(self):
        commit_time = str(timezone.now().isoformat())
        commit1 = FeederTestHelper.create_commit(1, [], 'user1', 'user1@test.com', commit_time, commit_time)
        commit2 = FeederTestHelper.create_commit(2, [1], 'user1', 'user1@test.com', commit_time, commit_time)
        commit3 = FeederTestHelper.create_commit(3, [2], 'user1', 'user1@test.com', commit_time, commit_time)

        commits = [commit1, commit2, commit3]

        GitFeederController.insert_parents(commits, self.git_project1)


    def test_insert_diffs_correctly(self):
        commit_time = str(timezone.now().isoformat())
        git_commit1 = GitCommitEntry.objects.create(
            project=self.git_project1,
            commit_hash=FeederTestHelper.hash_string(1),
            author=self.git_user1,
            author_date=commit_time,
            committer=self.git_user1,
            committer_date=commit_time
        )

        git_commit2 = GitCommitEntry.objects.create(
            project=self.git_project1,
            commit_hash=FeederTestHelper.hash_string(2),
            author=self.git_user1,
            author_date=commit_time,
            committer=self.git_user1,
            committer_date=commit_time
        )

        diff1 = FeederTestHelper.create_diff(2, 1, 'diff-content')

        GitFeederController.insert_diffs([diff1], self.git_project1)

        self.assertEqual(1, GitDiffEntry.objects.all().count())
        self.assertEqual('0000100001000010000100001000010000100001', GitDiffEntry.objects.all().first().commit_parent.commit_hash)
        self.assertEqual('0000200002000020000200002000020000200002', GitDiffEntry.objects.all().first().commit_son.commit_hash)

    def test_insert_diffs_no_son(self):
        commit_time = str(timezone.now().isoformat())
        git_commit1 = GitCommitEntry.objects.create(
            project=self.git_project1,
            commit_hash=FeederTestHelper.hash_string(1),
            author=self.git_user1,
            author_date=commit_time,
            committer=self.git_user1,
            committer_date=commit_time
        )

        diff1 = FeederTestHelper.create_diff(2, 1, 'diff-content')

        GitFeederController.insert_diffs([diff1], self.git_project1)

        self.assertEqual(0, GitDiffEntry.objects.all().count())

    def test_insert_diffs_no_parent(self):
        commit_time = str(timezone.now().isoformat())
        git_commit1 = GitCommitEntry.objects.create(
            project=self.git_project1,
            commit_hash=FeederTestHelper.hash_string(2),
            author=self.git_user1,
            author_date=commit_time,
            committer=self.git_user1,
            committer_date=commit_time
        )

        diff1 = FeederTestHelper.create_diff(2, 1, 'diff-content')

        GitFeederController.insert_diffs([diff1], self.git_project1)

        self.assertEqual(0, GitDiffEntry.objects.all().count())


    def test_insert_reports_with_existing_worker(self):
        reports = FeederTestHelper.get_default_report(1)

        self.assertEqual(0, FeedEntry.objects.all().count())

        GitFeederController.insert_reports(self.user1, reports)

        self.assertEqual(1, FeedEntry.objects.all().count())
        self.assertEqual(1, FeedEntry.objects.filter(worker=self.worker1).count())

        group_obj = FeedEntry.objects.filter(worker=self.worker1).first().command_group.as_object()

        self.assertEqual(1, len(group_obj['command_sets']))
        self.assertEqual(1, len(group_obj['command_sets'][0]['commands']))
        self.assertEqual(u'command0 arg1 arg2', group_obj['command_sets'][0]['commands'][0]['command'])
        self.assertEqual(0, group_obj['command_sets'][0]['commands'][0]['order'])
        self.assertEqual(0, group_obj['command_sets'][0]['commands'][0]['result']['status'])
        self.assertEqual(u'default-out', group_obj['command_sets'][0]['commands'][0]['result']['out'])
        self.assertEqual(u'default-error', group_obj['command_sets'][0]['commands'][0]['result']['error'])


    def test_insert_reports_with_user_but_not_worker(self):
        reports = FeederTestHelper.get_default_report(2)

        self.assertEqual(0, FeedEntry.objects.all().count())

        GitFeederController.insert_reports(self.user2, reports)

        self.assertEqual(1, FeedEntry.objects.all().count())
        self.assertEqual(0, FeedEntry.objects.filter(worker=self.worker1).count())

        group_obj = FeedEntry.objects.all().first().command_group.as_object()

        self.assertEqual(1, len(group_obj['command_sets']))
        self.assertEqual(2, len(group_obj['command_sets'][0]['commands']))
        self.assertEqual(u'command0 arg1 arg2', group_obj['command_sets'][0]['commands'][0]['command'])
        self.assertEqual(0, group_obj['command_sets'][0]['commands'][0]['order'])
        self.assertEqual(0, group_obj['command_sets'][0]['commands'][0]['result']['status'])
        self.assertEqual(u'default-out', group_obj['command_sets'][0]['commands'][0]['result']['out'])
        self.assertEqual(u'default-error', group_obj['command_sets'][0]['commands'][0]['result']['error'])

        self.assertEqual(u'command1 arg1 arg2', group_obj['command_sets'][0]['commands'][1]['command'])
        self.assertEqual(1, group_obj['command_sets'][0]['commands'][1]['order'])
        self.assertEqual(0, group_obj['command_sets'][0]['commands'][1]['result']['status'])
        self.assertEqual(u'default-out', group_obj['command_sets'][0]['commands'][1]['result']['out'])
        self.assertEqual(u'default-error', group_obj['command_sets'][0]['commands'][1]['result']['error'])

    def test_insert_reports_with_anonimous_user_and_not_worker(self):
        anonymous = AnonymousUser()
        reports = FeederTestHelper.get_default_report(3)

        self.assertEqual(0, FeedEntry.objects.all().count())

        GitFeederController.insert_reports(anonymous, reports)

        self.assertEqual(1, FeedEntry.objects.all().count())
        self.assertEqual(0, FeedEntry.objects.filter(worker=self.worker1).count())

        group_obj = FeedEntry.objects.all().first().command_group.as_object()

        self.assertEqual(1, len(group_obj['command_sets']))
        self.assertEqual(3, len(group_obj['command_sets'][0]['commands']))
        self.assertEqual(u'command0 arg1 arg2', group_obj['command_sets'][0]['commands'][0]['command'])
        self.assertEqual(0, group_obj['command_sets'][0]['commands'][0]['order'])
        self.assertEqual(0, group_obj['command_sets'][0]['commands'][0]['result']['status'])
        self.assertEqual(u'default-out', group_obj['command_sets'][0]['commands'][0]['result']['out'])
        self.assertEqual(u'default-error', group_obj['command_sets'][0]['commands'][0]['result']['error'])

        self.assertEqual(u'command1 arg1 arg2', group_obj['command_sets'][0]['commands'][1]['command'])
        self.assertEqual(1, group_obj['command_sets'][0]['commands'][1]['order'])
        self.assertEqual(0, group_obj['command_sets'][0]['commands'][1]['result']['status'])
        self.assertEqual(u'default-out', group_obj['command_sets'][0]['commands'][1]['result']['out'])
        self.assertEqual(u'default-error', group_obj['command_sets'][0]['commands'][1]['result']['error'])

        self.assertEqual(u'command2 arg1 arg2', group_obj['command_sets'][0]['commands'][2]['command'])
        self.assertEqual(2, group_obj['command_sets'][0]['commands'][2]['order'])
        self.assertEqual(0, group_obj['command_sets'][0]['commands'][2]['result']['status'])
        self.assertEqual(u'default-out', group_obj['command_sets'][0]['commands'][2]['result']['out'])
        self.assertEqual(u'default-error', group_obj['command_sets'][0]['commands'][2]['result']['error'])


    def test_insert_branch_trails(self):
        commit_time = str(timezone.now().isoformat())
        git_commit1 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash=FeederTestHelper.hash_string(1), author=self.git_user1, author_date=commit_time, committer=self.git_user1, committer_date=commit_time)
        git_commit2 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash=FeederTestHelper.hash_string(2), author=self.git_user1, author_date=commit_time, committer=self.git_user1, committer_date=commit_time)
        git_commit3 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash=FeederTestHelper.hash_string(3), author=self.git_user1, author_date=commit_time, committer=self.git_user1, committer_date=commit_time)
        git_commit4 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash=FeederTestHelper.hash_string(4), author=self.git_user1, author_date=commit_time, committer=self.git_user1, committer_date=commit_time)
        git_commit5 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash=FeederTestHelper.hash_string(5), author=self.git_user1, author_date=commit_time, committer=self.git_user1, committer_date=commit_time)
        git_commit6 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash=FeederTestHelper.hash_string(6), author=self.git_user1, author_date=commit_time, committer=self.git_user1, committer_date=commit_time)
        git_commit7 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash=FeederTestHelper.hash_string(7), author=self.git_user1, author_date=commit_time, committer=self.git_user1, committer_date=commit_time)
        git_commit8 = GitCommitEntry.objects.create(project=self.git_project1, commit_hash=FeederTestHelper.hash_string(8), author=self.git_user1, author_date=commit_time, committer=self.git_user1, committer_date=commit_time)

        branch1 = GitBranchEntry.objects.create(project=self.git_project1, name='branch1', commit=git_commit4)
        branch2 = GitBranchEntry.objects.create(project=self.git_project1, name='branch2', commit=git_commit8)

        commits1 = []
        commits1.append(FeederTestHelper.create_commit(1, [],  'user1', 'user1@test.com', self.time, self.time))
        commits1.append(FeederTestHelper.create_commit(2, [1], 'user1', 'user1@test.com', self.time, self.time))
        commits1.append(FeederTestHelper.create_commit(3, [2], 'user1', 'user1@test.com', self.time, self.time))
        commits1.append(FeederTestHelper.create_commit(4, [3], 'user1', 'user1@test.com', self.time, self.time))

        commits2 = []
        commits2.append(FeederTestHelper.create_commit(5, [],  'user1', 'user1@test.com', self.time, self.time))
        commits2.append(FeederTestHelper.create_commit(6, [5], 'user1', 'user1@test.com', self.time, self.time))
        commits2.append(FeederTestHelper.create_commit(7, [6], 'user1', 'user1@test.com', self.time, self.time))
        commits2.append(FeederTestHelper.create_commit(8, [7], 'user1', 'user1@test.com', self.time, self.time))

        trail1 = []
        trail1.append(1)
        trail1.append(2)
        trail1.append(3)
        trail1.append(4)

        trail2 = []
        trail2.append(5)
        trail2.append(6)
        trail2.append(7)
        trail2.append(8)

        branch_list = []
        branch_list.append(FeederTestHelper.create_branch('branch1', 4, 'branch1', 3, 2, trail1, 'content'))
        branch_list.append(FeederTestHelper.create_branch('branch2', 8, 'branch1', 4, 1, trail2, 'content'))

        self.assertEqual(0, GitBranchTrailEntry.objects.all().count())

        GitFeederController.insert_branch_trails(branch_list, self.git_project1)

        self.assertEqual(8, GitBranchTrailEntry.objects.all().count())
        self.assertEqual(1, GitBranchTrailEntry.objects.filter(commit__commit_hash='0000100001000010000100001000010000100001', branch__name='branch1', project=self.git_project1).count())
        self.assertEqual(1, GitBranchTrailEntry.objects.filter(commit__commit_hash='0000200002000020000200002000020000200002', branch__name='branch1', project=self.git_project1).count())
        self.assertEqual(1, GitBranchTrailEntry.objects.filter(commit__commit_hash='0000300003000030000300003000030000300003', branch__name='branch1', project=self.git_project1).count())
        self.assertEqual(1, GitBranchTrailEntry.objects.filter(commit__commit_hash='0000400004000040000400004000040000400004', branch__name='branch1', project=self.git_project1).count())
        self.assertEqual(1, GitBranchTrailEntry.objects.filter(commit__commit_hash='0000500005000050000500005000050000500005', branch__name='branch2', project=self.git_project1).count())
        self.assertEqual(1, GitBranchTrailEntry.objects.filter(commit__commit_hash='0000600006000060000600006000060000600006', branch__name='branch2', project=self.git_project1).count())
        self.assertEqual(1, GitBranchTrailEntry.objects.filter(commit__commit_hash='0000700007000070000700007000070000700007', branch__name='branch2', project=self.git_project1).count())
        self.assertEqual(1, GitBranchTrailEntry.objects.filter(commit__commit_hash='0000800008000080000800008000080000800008', branch__name='branch2', project=self.git_project1).count())
