""" Git Feed Views reports tests """

from django.test import TestCase
from django.test import Client
from django.conf import settings
from django.utils import timezone
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
from app.logic.commandrepo.models.CommandModel import CommandEntry
from app.logic.commandrepo.models.CommandResultModel import CommandResultEntry
from app.logic.httpcommon import res
from datetime import timedelta
import json
import os
import hashlib
import shutil
import datetime

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

        self.branch1 = FeederTestHelper.create_branch('master', 1, 'master', 1, 1, [1], 'merge-target-content')

    def tearDown(self):
        pass

    def test_report_ok(self):
        reports = []

        report = {}
        report['commands'] = []

        command = {}
        command['command'] = ['command1', 'arg1', 'arg2']
        command['result'] = {}
        command['result']['error'] = 'error-text-1'
        command['result']['out'] = 'out-text-1'
        command['result']['status'] = 0
        command['result']['start_time'] = datetime.datetime.utcnow().isoformat()
        command['result']['finish_time'] = datetime.datetime.utcnow().isoformat()

        report['commands'].append(command)
        reports.append(report)

        obj = {}
        obj['reports'] = reports

        resp = self.client.post(
            '/main/feed/commit/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(obj),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual('Only reports added', resp_obj['message'])

        reports_entry = CommandGroupEntry.objects.all()
        self.assertEqual(1, len(reports_entry))

        sets_entry = CommandSetEntry.objects.all()
        self.assertEqual(1, len(sets_entry))

        self.assertEqual(reports_entry[0], sets_entry[0].group)

        comm_entry = CommandEntry.objects.all().first()
        self.assertEqual('["command1", "arg1", "arg2"]', comm_entry.command)

        comm_result_entry = CommandResultEntry.objects.all().first()

        self.assertEqual('error-text-1', comm_result_entry.error)
        self.assertEqual('out-text-1', comm_result_entry.out)
        self.assertEqual(0, comm_result_entry.status)

        self.assertEqual(sets_entry[0], comm_entry.command_set)


    def test_many_reports(self):
        report_1 = FeederTestHelper.get_default_report()
        report_2 = FeederTestHelper.get_default_report()

        obj = {}
        obj['reports'] = report_1

        resp = self.client.post(
            '/main/feed/commit/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(obj),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual('Only reports added', resp_obj['message'])

        obj['reports'] = report_2

        resp = self.client.post(
            '/main/feed/commit/project/{0}/'.format(self.git_project1.id),
            data = json.dumps(obj),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual('Only reports added', resp_obj['message'])

        reports_entry = CommandGroupEntry.objects.all()
        self.assertEqual(2, len(reports_entry))

        sets_entry = CommandSetEntry.objects.all()
        self.assertEqual(2, len(sets_entry))

        commands_entry = CommandEntry.objects.all()
        self.assertEqual(2, len(commands_entry))
