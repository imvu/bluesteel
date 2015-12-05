""" Git Feed Views branch tests """

from django.test import TestCase
from django.test import Client
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
# Move view functions on ViewsJsonGitFeeder to a GitFeeder Controller. It is missing!
from app.presenter.views.json import ViewJsonGitFeeder
from app.logic.gitrepo.models.GitProjectModel import GitProjectEntry
from app.logic.gitrepo.models.GitUserModel import GitUserEntry
from app.logic.gitrepo.models.GitCommitModel import GitCommitEntry
from app.logic.gitrepo.models.GitParentModel import GitParentEntry
from app.logic.gitrepo.models.GitDiffModel import GitDiffEntry
from app.logic.gitrepo.models.GitBranchModel import GitBranchEntry
from app.logic.gitrepo.models.GitBranchTrailModel import GitBranchTrailEntry
from app.logic.gitrepo.models.GitBranchMergeTargetModel import GitBranchMergeTargetEntry
from app.logic.gitfeeder.helper import FeederTestHelper
from app.logic.httpcommon import res
from app.logic.logger.models.LogModel import LogEntry
from datetime import timedelta
import json
import os
import hashlib
import shutil

# Create your tests here.

class GitFeedViewsBranchTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user('user1@test.com', 'user1@test.com', 'pass1')
        self.user1.save()

        self.git_project1 = GitProjectEntry.objects.create(url='http://test/')
        self.git_user1 = GitUserEntry.objects.create(
            project=self.git_project1,
            name='user1',
            email='user1@test.com'
        )


    def tearDown(self):
        pass

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
        branch1 = FeederTestHelper.create_branch('master', 1, [FeederTestHelper.hash_string(1)], 'master')

        ViewJsonGitFeeder.insert_branches(self.user1, [branch1], self.git_project1)

        self.assertEqual(1, GitBranchEntry.objects.all().count())
        self.assertEqual('master', GitBranchEntry.objects.all().first().name)

        self.assertEqual(0, GitBranchTrailEntry.objects.all().count())

        self.assertEqual(1, GitCommitEntry.objects.all().count())
        self.assertEqual(FeederTestHelper.hash_string(1), GitCommitEntry.objects.all().first().commit_hash)

        self.assertEqual(0, LogEntry.objects.all().count())

    def test_insert_branch_and_log_because_branch_commit_not_found(self):
        commit_time = str(timezone.now().isoformat())
        commit1 = FeederTestHelper.create_commit(1, [], 'user1', 'user1@test.com', commit_time, commit_time)

        branch1 = FeederTestHelper.create_branch('master', 1, [FeederTestHelper.hash_string(1)], 'master')

        ViewJsonGitFeeder.insert_branches(self.user1, [branch1], self.git_project1)

        self.assertEqual(0, GitBranchTrailEntry.objects.all().count())
        self.assertEqual(0, GitCommitEntry.objects.all().count())
        self.assertEqual(0, GitBranchEntry.objects.all().count())
        self.assertEqual(1, LogEntry.objects.all().count())

        log = LogEntry.objects.all().first()
        self.assertEqual(LogEntry.ERROR, log.log_type)
        self.assertEqual('Branch commit 0000100001000010000100001000010000100001 not found!', log.message)


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
        commit2 = FeederTestHelper.create_commit(2, [FeederTestHelper.hash_string(1)], 'user1', 'user1@test.com', commit_time, commit_time)
        commit3 = FeederTestHelper.create_commit(3, [FeederTestHelper.hash_string(2)], 'user1', 'user1@test.com', commit_time, commit_time)

        commits = [commit1, commit2, commit3]

        ViewJsonGitFeeder.insert_parents(self.user1, commits, self.git_project1)

        self.assertEqual(0, LogEntry.objects.all().count())
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

        self.assertEqual(0, LogEntry.objects.all().count())
        self.assertEqual(2, GitParentEntry.objects.all().count())
        self.assertEqual(1, GitParentEntry.objects.filter(parent__commit_hash=FeederTestHelper.hash_string(1), son__commit_hash=FeederTestHelper.hash_string(2)).count())
        self.assertEqual(1, GitParentEntry.objects.filter(parent__commit_hash=FeederTestHelper.hash_string(2), son__commit_hash=FeederTestHelper.hash_string(3)).count())

        commit1 = FeederTestHelper.create_commit(1, [], 'user1', 'user1@test.com', commit_time, commit_time)
        commit2 = FeederTestHelper.create_commit(2, [FeederTestHelper.hash_string(1)], 'user1', 'user1@test.com', commit_time, commit_time)
        commit3 = FeederTestHelper.create_commit(3, [FeederTestHelper.hash_string(2)], 'user1', 'user1@test.com', commit_time, commit_time)

        commits = [commit1, commit2, commit3]

        ViewJsonGitFeeder.insert_parents(self.user1, commits, self.git_project1)

        self.assertEqual(0, LogEntry.objects.all().count())
        self.assertEqual(2, GitParentEntry.objects.all().count())
        self.assertEqual(1, GitParentEntry.objects.filter(parent__commit_hash=FeederTestHelper.hash_string(1), son__commit_hash=FeederTestHelper.hash_string(2)).count())
        self.assertEqual(1, GitParentEntry.objects.filter(parent__commit_hash=FeederTestHelper.hash_string(2), son__commit_hash=FeederTestHelper.hash_string(3)).count())

    def test_insert_parents_with_no_commits_present(self):
        commit_time = str(timezone.now().isoformat())
        commit1 = FeederTestHelper.create_commit(1, [], 'user1', 'user1@test.com', commit_time, commit_time)
        commit2 = FeederTestHelper.create_commit(2, [FeederTestHelper.hash_string(1)], 'user1', 'user1@test.com', commit_time, commit_time)
        commit3 = FeederTestHelper.create_commit(3, [FeederTestHelper.hash_string(2)], 'user1', 'user1@test.com', commit_time, commit_time)

        commits = [commit1, commit2, commit3]

        ViewJsonGitFeeder.insert_parents(self.user1, commits, self.git_project1)

        self.assertEqual(2, LogEntry.objects.all().count())
        self.assertEqual(LogEntry.ERROR, LogEntry.objects.all()[0].log_type)
        self.assertEqual(LogEntry.ERROR, LogEntry.objects.all()[1].log_type)


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

        diff1 = FeederTestHelper.create_diff(FeederTestHelper.hash_string(2), FeederTestHelper.hash_string(1), 'diff-content')

        ViewJsonGitFeeder.insert_diffs(self.user1, [diff1], self.git_project1)

        self.assertEqual(1, GitDiffEntry.objects.all().count())
        self.assertEqual(0, LogEntry.objects.all().count())
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

        diff1 = FeederTestHelper.create_diff(FeederTestHelper.hash_string(2), FeederTestHelper.hash_string(1), 'diff-content')

        ViewJsonGitFeeder.insert_diffs(self.user1, [diff1], self.git_project1)

        self.assertEqual(0, GitDiffEntry.objects.all().count())
        self.assertEqual(1, LogEntry.objects.all().count())
        self.assertEqual(LogEntry.ERROR, LogEntry.objects.all().first().log_type)
        self.assertEqual('Commit son 0000200002000020000200002000020000200002 not found while inserting diffs!', LogEntry.objects.all().first().message)

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

        diff1 = FeederTestHelper.create_diff(FeederTestHelper.hash_string(2), FeederTestHelper.hash_string(1), 'diff-content')

        ViewJsonGitFeeder.insert_diffs(self.user1, [diff1], self.git_project1)

        self.assertEqual(0, GitDiffEntry.objects.all().count())
        self.assertEqual(1, LogEntry.objects.all().count())
        self.assertEqual(LogEntry.ERROR, LogEntry.objects.all().first().log_type)
        self.assertEqual(u'Commit parent 0000100001000010000100001000010000100001 not found while inserting diffs!', LogEntry.objects.all().first().message)
