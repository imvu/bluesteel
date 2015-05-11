""" Git Feed Views reports tests """

from django.test import TestCase
from django.test import Client
from django.conf import settings
from django.utils import timezone
from app.service.gitrepo.models.GitProjectModel import GitProjectEntry
from app.service.gitrepo.models.GitUserModel import GitUserEntry
from app.service.gitrepo.models.GitCommitModel import GitCommitEntry
from app.service.gitrepo.models.GitParentModel import GitParentEntry
from app.service.gitrepo.models.GitDiffModel import GitDiffEntry
from app.service.gitrepo.models.GitBranchModel import GitBranchEntry
from app.service.gitrepo.models.GitBranchTrailModel import GitBranchTrailEntry
from app.service.gitfeeder.helper import FeederTestHelper
from app.util.commandrepo.models.CommandReportModel import CommandReportEntry
from app.util.commandrepo.models.CommandSetModel import CommandSetEntry
from app.util.commandrepo.models.CommandModel import CommandEntry
from app.util.httpcommon import res
from datetime import timedelta
import json
import os
import hashlib
import shutil

class GitFeedViewsReportsTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.git_project1 = GitProjectEntry.objects.create(url='http://test/')
        self.git_user1 = GitUserEntry.objects.create(
            project=self.git_project1,
            name='user1',
            email='user1@test.com'
        )

        self.commit_time = str(timezone.now().isoformat())
        self.commit1 = FeederTestHelper.create_commit(1, [], 'user1', 'user1@test.com', self.commit_time, self.commit_time)
        self.commit2 = FeederTestHelper.create_commit(2, [], 'user1', 'user1@test.com', self.commit_time, self.commit_time)

        self.merge_target = FeederTestHelper.create_merge_target('master', FeederTestHelper.hash_string(1), FeederTestHelper.hash_string(1), 'merge-target-content')

        self.branch1 = FeederTestHelper.create_branch('master', 1, [FeederTestHelper.hash_string(1)], self.merge_target)

    def tearDown(self):
        pass

    def test_report_ok(self):
        reports = []

        report = {}
        report['commands'] = []

        command = {}
        command['command'] = ['command1', 'arg1', 'arg2']
        command['error'] = 'error-text-1'
        command['out'] = 'out-text-1'
        command['status'] = 'OK'

        report['commands'].append(command)
        reports.append(report)

        obj = {}
        obj['reports'] = reports

        resp = self.client.post(
            '/gitfeeder/feed/commit/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(obj),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual('Only reports added', resp_obj['message'])

        reports_entry = CommandReportEntry.objects.all()
        self.assertEqual(1, len(reports_entry))

        sets_entry = CommandSetEntry.objects.all()
        self.assertEqual(1, len(sets_entry))

        self.assertEqual(reports_entry[0], sets_entry[0].report)

        comm_entry = CommandEntry.objects.all().first()
        self.assertEqual('["command1", "arg1", "arg2"]', comm_entry.command)
        self.assertEqual('error-text-1', comm_entry.error)
        self.assertEqual('out-text-1', comm_entry.out)
        self.assertEqual(CommandEntry.OK, comm_entry.status)

        self.assertEqual(sets_entry[0], comm_entry.command_set)


    def test_many_reports(self):
        report_1 = FeederTestHelper.get_default_report()
        report_2 = FeederTestHelper.get_default_report()

        obj = {}
        obj['reports'] = report_1

        resp = self.client.post(
            '/gitfeeder/feed/commit/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(obj),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual('Only reports added', resp_obj['message'])

        obj['reports'] = report_2

        resp = self.client.post(
            '/gitfeeder/feed/commit/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(obj),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual('Only reports added', resp_obj['message'])

        reports_entry = CommandReportEntry.objects.all()
        self.assertEqual(2, len(reports_entry))

        sets_entry = CommandSetEntry.objects.all()
        self.assertEqual(2, len(sets_entry))

        commands_entry = CommandEntry.objects.all()
        self.assertEqual(2, len(commands_entry))
