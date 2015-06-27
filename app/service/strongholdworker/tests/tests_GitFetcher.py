""" Git Fetch tests """

from django.test import TestCase
from django.conf import settings
from django.utils import timezone
from django.utils.six import StringIO
from app.service.strongholdworker.download.GitFetcher import GitFetcher
from datetime import timedelta
import os
import json
import hashlib
import shutil
import mock

class GitFetcherTestCase(TestCase):

    def setUp(self):
        self.tmp_folder = os.path.join(settings.TMP_ROOT)

        if not os.path.exists(self.tmp_folder):
            os.makedirs(self.tmp_folder)

        self.obj = {}
        self.obj['git'] = {}
        self.obj['git']['project'] = {}
        self.obj['git']['project']['current_working_directory'] = self.tmp_folder
        self.obj['git']['project']['tmp_directory'] = 'gitfetcher'
        self.obj['git']['project']['archive'] = 'proj-28-0123ABC'
        self.obj['git']['project']['name'] = 'test-repo'
        self.obj['git']['project']['url'] = 'git-url'
        self.obj['git']['branches'] = []
        self.obj['git']['clone'] = {}
        self.obj['git']['clone']['commands'] = []
        self.obj['git']['clone']['commands'].append(['git','clone','https://llorensmarti@bitbucket.org/llorensmarti/test-repo.git'])
        self.obj['git']['clone']['commands'].append(['git','submodule','update', '--init', '--recursive'])
        self.obj['git']['fetch'] = {}
        self.obj['git']['fetch']['commands'] = []
        self.obj['git']['fetch']['commands'].append(['git', 'reset', '--hard', 'origin/master'])
        self.obj['git']['fetch']['commands'].append(['git', 'clean', '-f', '-d', '-q'])
        self.obj['git']['fetch']['commands'].append(['git', 'pull', '-r', 'origin', 'master'])
        self.obj['git']['fetch']['commands'].append(['git', 'checkout', 'master'])
        self.obj['git']['fetch']['commands'].append(['git', 'submodule', 'update', '--init', '--recursive'])

        self.fetcher = GitFetcher()

    def tearDown(self):
        if os.path.exists(self.tmp_folder):
            shutil.rmtree(self.tmp_folder)

    def test_get_project_folder(self):
        path = '{0}/{1}/{2}'.format(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC')
        self.assertEqual(path, self.fetcher.get_archive_folder_path(self.obj))

    def test_is_project_folder_present(self):
        os.makedirs(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC'))
        self.assertTrue(self.fetcher.is_project_folder_present(self.obj))

    def test_is_not_project_folder_present(self):
        self.assertFalse(self.fetcher.is_project_folder_present(self.obj))

    def test_is_git_project_folder_present(self):
        os.makedirs(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC', 'project'))
        self.assertTrue(self.fetcher.is_git_project_folder_present(self.obj))

    def test_is_not_git_project_folder_present(self):
        os.makedirs(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC'))
        self.assertFalse(self.fetcher.is_git_project_folder_present(self.obj))

    def test_is_log_project_folder_present(self):
        os.makedirs(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC', 'log'))
        self.assertTrue(self.fetcher.is_log_project_folder_present(self.obj))

    def test_is_not_log_project_folder_present(self):
        os.makedirs(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC'))
        self.assertFalse(self.fetcher.is_log_project_folder_present(self.obj))

    def test_create_tmp_folder_for_git_project(self):
        self.fetcher.create_tmp_folder_for_git_project(self.obj)
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC', 'project')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC', 'log')))

    def test_create_tmp_folder_remove_previous_folder(self):
        os.makedirs(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC', 'folder-2'))
        self.fetcher.create_tmp_folder_for_git_project(self.obj)
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC', 'project')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC', 'log')))
        self.assertFalse(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC', 'folder-2')))

    def test_clear_log_folder(self):
        project_path = os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC')
        log_path = os.path.join(project_path, 'log')
        os.makedirs(log_path)
        file_log = open(os.path.join(log_path, 'log1.txt'), 'w')
        file_log.close()

        self.assertTrue(os.path.exists(os.path.join(log_path, 'log1.txt')))
        self.fetcher.clear_logs_folder(project_path)
        self.assertTrue(os.path.exists(log_path))
        self.assertFalse(os.path.exists(os.path.join(log_path, 'log1.txt')))

    @mock.patch('app.service.strongholdworker.download.GitFetcher.subprocess')
    def test_clone_project(self, mock_subprocess):
        self.fetcher.create_tmp_folder_for_git_project(self.obj)
        reports = self.fetcher.commands_clone_git_project(self.obj)
        mock_subprocess.check_call.assert_called_once(['git','clone','https://llorensmarti@bitbucket.org/llorensmarti/test-repo.git'])
        mock_subprocess.check_call.assert_called_once(['git','submodule','update', '--init', '--recursive'])
        self.assertEqual(2, mock_subprocess.check_call.call_count)

        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC', 'project')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC', 'log')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC', 'log', 'git_clone_stdout.txt')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC', 'log', 'git_clone_stderr.txt')))

        self.assertEqual(2, len(reports['commands']))

        self.assertEqual('OK', reports['commands'][0]['status'])
        self.assertEqual(['git', 'clone', 'https://llorensmarti@bitbucket.org/llorensmarti/test-repo.git'], reports['commands'][0]['command'])
        self.assertEqual('', reports['commands'][0]['error'])
        self.assertEqual('', reports['commands'][0]['out'])

        self.assertEqual('OK', reports['commands'][1]['status'])
        self.assertEqual(['git', 'submodule', 'update', '--init', '--recursive'], reports['commands'][1]['command'])
        self.assertEqual('', reports['commands'][1]['error'])
        self.assertEqual('', reports['commands'][1]['out'])


    @mock.patch('app.service.strongholdworker.download.GitFetcher.subprocess')
    def test_fetch_project(self, mock_subprocess):
        self.fetcher.create_tmp_folder_for_git_project(self.obj)
        reports = self.fetcher.commands_fetch_git_project(self.obj)
        mock_subprocess.check_call.assert_called_once(['git', 'reset', '--hard', 'origin/master'])
        mock_subprocess.check_call.assert_called_once(['git', 'clean', '-f', '-d', '-q'])
        mock_subprocess.check_call.assert_called_once(['git', 'pull', '-r', 'origin', 'master'])
        mock_subprocess.check_call.assert_called_once(['git', 'checkout', 'master'])
        mock_subprocess.check_call.assert_called_once(['git','submodule','update', '--init', '--recursive'])
        self.assertEqual(5, mock_subprocess.check_call.call_count)

        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC', 'project')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC', 'log')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC', 'log', 'git_clone_stdout.txt')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC', 'log', 'git_clone_stderr.txt')))

        self.assertEqual(5, len(reports['commands']))

        self.assertEqual('OK', reports['commands'][0]['status'])
        self.assertEqual(['git', 'reset', '--hard', 'origin/master'], reports['commands'][0]['command'])
        self.assertEqual('', reports['commands'][0]['error'])
        self.assertEqual('', reports['commands'][0]['out'])

        self.assertEqual('OK', reports['commands'][1]['status'])
        self.assertEqual(['git', 'clean', '-f', '-d', '-q'], reports['commands'][1]['command'])
        self.assertEqual('', reports['commands'][1]['error'])
        self.assertEqual('', reports['commands'][1]['out'])

        self.assertEqual('OK', reports['commands'][2]['status'])
        self.assertEqual(['git', 'pull', '-r', 'origin', 'master'], reports['commands'][2]['command'])
        self.assertEqual('', reports['commands'][2]['error'])
        self.assertEqual('', reports['commands'][2]['out'])

        self.assertEqual('OK', reports['commands'][3]['status'])
        self.assertEqual(['git', 'checkout', 'master'], reports['commands'][3]['command'])
        self.assertEqual('', reports['commands'][3]['error'])
        self.assertEqual('', reports['commands'][3]['out'])

        self.assertEqual('OK', reports['commands'][4]['status'])
        self.assertEqual(['git','submodule','update', '--init', '--recursive'], reports['commands'][4]['command'])
        self.assertEqual('', reports['commands'][4]['error'])
        self.assertEqual('', reports['commands'][4]['out'])

    @mock.patch('app.service.strongholdworker.download.GitFetcher.subprocess')
    def test_get_branch_names(self, mock_subprocess):
        self.fetcher.create_tmp_folder_for_git_project(self.obj)
        reports = self.fetcher.commands_get_branch_names(self.obj)
        mock_subprocess.check_call.assert_called_once(['git', 'branch'])
        self.assertEqual(1, mock_subprocess.check_call.call_count)

        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC', 'project')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC', 'log')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC', 'log', 'git_clone_stdout.txt')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC', 'log', 'git_clone_stderr.txt')))

        self.assertEqual(1, len(reports['commands']))

        self.assertEqual('OK', reports['commands'][0]['status'])
        self.assertEqual(['git', 'branch'], reports['commands'][0]['command'])
        self.assertEqual('', reports['commands'][0]['error'])
        self.assertEqual('', reports['commands'][0]['out'])


    def test_extract_branch_names_correct(self):
        report1 = {}
        report1['status'] = 'OK'
        report1['command'] = ['git', 'branch']
        report1['out'] = ' * master\n branch-1\n\n'
        report1['error'] = ''

        report2 = {}
        report2['status'] = 'OK'
        report2['command'] = ['git', 'status']
        report2['out'] = 'Hey!!!'
        report2['error'] = ''

        obj = {}
        obj['status'] = True
        obj['commands'] = []
        obj['commands'].append(report1)
        obj['commands'].append(report2)

        branch_names = self.fetcher.extract_branch_names_from_report(obj)

        self.assertEqual(2, len(branch_names))
        self.assertEqual('master', branch_names[0])
        self.assertEqual('branch-1', branch_names[1])

    def test_extract_branch_names_empty_because_error(self):
        report1 = {}
        report1['status'] = 'ERROR'
        report1['command'] = ['git', 'branch']
        report1['out'] = ''
        report1['error'] = 'Some error'

        obj = {}
        obj['status'] = False
        obj['commands'] = []
        obj['commands'].append(report1)

        branch_names = self.fetcher.extract_branch_names_from_report(obj)

        self.assertEqual(0, len(branch_names))

    @mock.patch('app.service.strongholdworker.download.GitFetcher.subprocess')
    def test_commands_get_branch_names_and_hashes(self, mock_subprocess):
        branch_names = ['master', 'branch-1', 'branch-2']
        self.fetcher.create_tmp_folder_for_git_project(self.obj)
        reports = self.fetcher.commands_get_branch_names_and_hashes(self.obj, branch_names)
        mock_subprocess.check_call.assert_called_once(['git', 'rev-parse', 'master'])
        mock_subprocess.check_call.assert_called_once(['git', 'rev-parse', 'branch-1'])
        mock_subprocess.check_call.assert_called_once(['git', 'rev-parse', 'branch-2'])
        self.assertEqual(3, mock_subprocess.check_call.call_count)

        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC', 'project')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC', 'log')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC', 'log', 'git_clone_stdout.txt')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC', 'log', 'git_clone_stderr.txt')))

        self.assertEqual(3, len(reports['commands']))

        self.assertEqual('OK', reports['commands'][0]['status'])
        self.assertEqual(['git', 'rev-parse', 'master'], reports['commands'][0]['command'])
        self.assertEqual('', reports['commands'][0]['error'])
        self.assertEqual('', reports['commands'][0]['out'])

        self.assertEqual('OK', reports['commands'][1]['status'])
        self.assertEqual(['git', 'rev-parse', 'branch-1'], reports['commands'][1]['command'])
        self.assertEqual('', reports['commands'][1]['error'])
        self.assertEqual('', reports['commands'][1]['out'])

        self.assertEqual('OK', reports['commands'][2]['status'])
        self.assertEqual(['git', 'rev-parse', 'branch-2'], reports['commands'][2]['command'])
        self.assertEqual('', reports['commands'][2]['error'])
        self.assertEqual('', reports['commands'][2]['out'])

    def test_extract_branch_names_and_hashes_correct(self):
        report1 = {}
        report1['status'] = 'OK'
        report1['command'] = ['git', 'rev-parse', 'master']
        report1['out'] = '0000100001000010000100001000010000100001'
        report1['error'] = ''

        report2 = {}
        report2['status'] = 'OK'
        report2['command'] = ['git', 'rev-parse', 'branch-1']
        report2['out'] = '0000200002000020000200002000020000200002'
        report2['error'] = ''

        obj = {}
        obj['status'] = True
        obj['commands'] = []
        obj['commands'].append(report1)
        obj['commands'].append(report2)

        branch_names = self.fetcher.extract_branch_names_hashes_from_report(obj)

        self.assertEqual(2, len(branch_names))
        self.assertEqual('master', branch_names[0]['name'])
        self.assertEqual('0000100001000010000100001000010000100001', branch_names[0]['hash'])
        self.assertEqual('branch-1', branch_names[1]['name'])
        self.assertEqual('0000200002000020000200002000020000200002', branch_names[1]['hash'])

    @mock.patch('app.service.strongholdworker.download.GitFetcher.subprocess')
    def test_commands_get_commits_from_branch(self, mock_subprocess):
        branch_name = 'branch-1'
        branch_hash = '0000100001000010000100001000010000100001'

        pretty_format = {}
        pretty_format['hash'] = '%H'
        pretty_format['parent_hashes'] = '%P'
        pretty_format['author'] = {}
        pretty_format['author']['name'] = '%an'
        pretty_format['author']['email'] = '%ae'
        pretty_format['author']['date'] = '%aI'
        pretty_format['committer'] = {}
        pretty_format['committer']['name'] = '%cn'
        pretty_format['committer']['email'] = '%ce'
        pretty_format['committer']['date'] = '%cI'

        pretty_string = '--pretty=format:{0},'.format(json.dumps(pretty_format))

        self.fetcher.create_tmp_folder_for_git_project(self.obj)
        reports = self.fetcher.commands_get_commits_from_branch(self.obj, branch_name)
        mock_subprocess.check_call.assert_called_once(['git', 'reset', '--hard'])
        mock_subprocess.check_call.assert_called_once(['git', 'clean', '-f', '-d', '-q'])
        mock_subprocess.check_call.assert_called_once(['git', 'checkout', 'branch-1'])
        mock_subprocess.check_call.assert_called_once(['git', 'log', '--first-parent', '--date=iso', pretty_string])
        self.assertEqual(4, mock_subprocess.check_call.call_count)

        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC', 'project')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC', 'log')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC', 'log', 'git_clone_stdout.txt')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC', 'log', 'git_clone_stderr.txt')))

        self.assertEqual(4, len(reports['commands']))

        self.assertEqual('OK', reports['commands'][0]['status'])
        self.assertEqual(['git', 'reset', '--hard'], reports['commands'][0]['command'])
        self.assertEqual('', reports['commands'][0]['error'])
        self.assertEqual('', reports['commands'][0]['out'])

        self.assertEqual('OK', reports['commands'][1]['status'])
        self.assertEqual(['git', 'clean', '-f', '-d', '-q'], reports['commands'][1]['command'])
        self.assertEqual('', reports['commands'][1]['error'])
        self.assertEqual('', reports['commands'][1]['out'])

        self.assertEqual('OK', reports['commands'][2]['status'])
        self.assertEqual(['git', 'checkout', 'branch-1'], reports['commands'][2]['command'])
        self.assertEqual('', reports['commands'][2]['error'])
        self.assertEqual('', reports['commands'][2]['out'])

        self.assertEqual('OK', reports['commands'][3]['status'])
        self.assertEqual(['git', 'log', '--first-parent', '--date=iso', pretty_string], reports['commands'][3]['command'])
        self.assertEqual('', reports['commands'][3]['error'])
        self.assertEqual('', reports['commands'][3]['out'])

    def test_extract_and_format_commits_from_report(self):
        report1 = {}
        report1['status'] = 'OK'
        report1['command'] = ['git', 'rev-parse', 'master']
        report1['out'] = '0000100001000010000100001000010000100001'
        report1['error'] = ''

        report2 = {}
        report2['status'] = 'OK'
        report2['command'] = ['git', 'log', '...']
        report2['out'] = '{\
                "hash":"0000100001000010000100001000010000100001",\
                "parent_hashes":"0000500005000050000500005000050000500005 0000200002000020000200002000020000200002",\
                "author": {\
                    "name":"llorensmarti",\
                    "email":"lgarcia@test.com",\
                    "date":"2015-03-08T23:13:33-07:00"\
                },\
                "committer": {\
                    "name":"llorensmarti2",\
                    "email":"lgarcia-2@test.com",\
                    "date":"2015-03-08T23:13:33-07:00"\
                }\
            },{\
                "hash":"0000200002000020000200002000020000200002",\
                "parent_hashes":"0000300003000030000300003000030000300003",\
                "author": {\
                    "name":"llorensmarti",\
                    "email":"lgarcia@test.com",\
                    "date":"2015-03-08T23:13:33-07:00"\
                },\
                "committer": {\
                    "name":"llorensmarti2",\
                    "email":"lgarcia-2@test.com",\
                    "date":"2015-03-08T23:13:33-07:00"\
                }\
            },'
        report2['error'] = ''

        obj = {}
        obj['status'] = True
        obj['commands'] = []
        obj['commands'].append(report1)
        obj['commands'].append(report2)

        commits = self.fetcher.extract_and_format_commits_from_report(obj)

        self.assertEqual(2, len(commits))

        self.assertEqual('0000100001000010000100001000010000100001', commits[0]['hash'])
        self.assertEqual(2, len(commits[0]['parent_hashes']))
        self.assertEqual('0000500005000050000500005000050000500005', commits[0]['parent_hashes'][0])
        self.assertEqual('0000200002000020000200002000020000200002', commits[0]['parent_hashes'][1])
        self.assertEqual('llorensmarti', commits[0]['author']['name'])
        self.assertEqual('lgarcia@test.com', commits[0]['author']['email'])
        self.assertEqual('2015-03-08T23:13:33-07:00', commits[0]['author']['date'])
        self.assertEqual('llorensmarti2', commits[0]['committer']['name'])
        self.assertEqual('lgarcia-2@test.com', commits[0]['committer']['email'])
        self.assertEqual('2015-03-08T23:13:33-07:00', commits[0]['committer']['date'])

        self.assertEqual('0000200002000020000200002000020000200002', commits[1]['hash'])
        self.assertEqual(1, len(commits[1]['parent_hashes']))
        self.assertEqual('0000300003000030000300003000030000300003', commits[1]['parent_hashes'][0])
        self.assertEqual('llorensmarti', commits[1]['author']['name'])
        self.assertEqual('lgarcia@test.com', commits[1]['author']['email'])
        self.assertEqual('2015-03-08T23:13:33-07:00', commits[1]['author']['date'])
        self.assertEqual('llorensmarti2', commits[1]['committer']['name'])
        self.assertEqual('lgarcia-2@test.com', commits[1]['committer']['email'])
        self.assertEqual('2015-03-08T23:13:33-07:00', commits[1]['committer']['date'])

    def test_trimmed_commits_not_found(self):
        commmit1 = {'hash' : '0000100001000010000100001000010000100001'}
        commmit2 = {'hash' : '0000200002000020000200002000020000200002'}
        commmit3 = {'hash' : '0000300003000030000300003000030000300003'}
        commmit4 = {'hash' : '0000400004000040000400004000040000400004'}

        commits = []
        commits.append(commmit1)
        commits.append(commmit2)
        commits.append(commmit3)
        commits.append(commmit4)

        branch1 = {}
        branch1['name'] = 'name-1'
        branch1['hash'] = '0000700007000070000700007000070000700007'
        branch1['merge_target'] = 'name-1'

        branch2 = {}
        branch2['name'] = 'name-2'
        branch2['hash'] = '0000800008000080000800008000080000800008'
        branch2['merge_target'] = 'name-1'

        branch3 = {}
        branch3['name'] = 'name-3'
        branch3['hash'] = '0000900009000090000900009000090000900009'
        branch3['merge_target'] = 'name-1'

        known_branches = []
        known_branches.append(branch1)
        known_branches.append(branch2)
        known_branches.append(branch3)

        res = self.fetcher.trim_commit_list_with_known_branches(commits, known_branches)

        self.assertEqual(4, len(res))
        self.assertEqual('0000100001000010000100001000010000100001', res[0]['hash'])
        self.assertEqual('0000200002000020000200002000020000200002', res[1]['hash'])
        self.assertEqual('0000300003000030000300003000030000300003', res[2]['hash'])
        self.assertEqual('0000400004000040000400004000040000400004', res[3]['hash'])

    def test_trimmed_commits_found(self):
        commmit1 = {'hash' : '0000100001000010000100001000010000100001'}
        commmit2 = {'hash' : '0000200002000020000200002000020000200002'}
        commmit3 = {'hash' : '0000300003000030000300003000030000300003'}
        commmit4 = {'hash' : '0000400004000040000400004000040000400004'}

        commits = []
        commits.append(commmit1)
        commits.append(commmit2)
        commits.append(commmit3)
        commits.append(commmit4)

        branch1 = {}
        branch1['name'] = 'name-1'
        branch1['hash'] = '0000700007000070000700007000070000700007'
        branch1['merge_target'] = 'name-1'

        branch2 = {}
        branch2['name'] = 'name-2'
        branch2['hash'] = '0000800008000080000800008000080000800008'
        branch2['merge_target'] = 'name-1'

        branch3 = {}
        branch3['name'] = 'name-3'
        branch3['hash'] = '0000200002000020000200002000020000200002'
        branch3['merge_target'] = 'name-1'

        known_branches = []
        known_branches.append(branch1)
        known_branches.append(branch2)
        known_branches.append(branch3)

        res = self.fetcher.trim_commit_list_with_known_branches(commits, known_branches)

        self.assertEqual(2, len(res))
        self.assertEqual('0000100001000010000100001000010000100001', res[0]['hash'])
        self.assertEqual('0000200002000020000200002000020000200002', res[1]['hash'])

    @mock.patch('app.service.strongholdworker.download.GitFetcher.subprocess')
    def test_commands_get_shared_commit_between_branches(self, mock_subprocess):
        branch1 = {}
        branch1['name'] = 'branch-1'
        branch1['hash'] = '0000100001000010000100001000010000100001'

        branch2 = {}
        branch2['name'] = 'branch-2'
        branch2['hash'] = '0000200002000020000200002000020000200002'

        self.fetcher.create_tmp_folder_for_git_project(self.obj)
        reports = self.fetcher.commands_get_fork_commit_between_branches(self.obj, branch1, branch2)
        mock_subprocess.check_call.assert_called_once(['git', 'merge-base', branch1['hash'], branch2['hash']])
        self.assertEqual(1, mock_subprocess.check_call.call_count)

        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC', 'project')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC', 'log')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC', 'log', 'git_clone_stdout.txt')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC', 'log', 'git_clone_stderr.txt')))

        self.assertEqual(1, len(reports['commands']))

        self.assertEqual('OK', reports['commands'][0]['status'])
        self.assertEqual(['git', 'merge-base', branch1['hash'], branch2['hash']], reports['commands'][0]['command'])
        self.assertEqual('', reports['commands'][0]['error'])
        self.assertEqual('', reports['commands'][0]['out'])

    def test_get_merge_target_from_branch_list_found_in_known(self):
        branch_merge_target = {}
        branch_merge_target['name'] = 'b-k-2'
        branch_merge_target['hash'] = '0000300003000030000300003000030000300003'

        branch_known_1 = {}
        branch_known_1['name'] = 'b-k-1'
        branch_known_1['hash'] = '0000200002000020000200002000020000200002'
        branch_known_1['merge_target'] = {}
        branch_known_1['merge_target']['name'] = 'b-k-1-5'
        branch_known_1['merge_target']['hash'] = '0000800008000080000800008000080000800008'

        branch_known_2 = {}
        branch_known_2['name'] = 'b-k-2'
        branch_known_2['hash'] = '0000300003000030000300003000030000300003'
        branch_known_2['merge_target'] = {}
        branch_known_2['merge_target']['name'] = 'b-k-2-5'
        branch_known_2['merge_target']['hash'] = '0000700007000070000700007000070000700007'

        branch_extracted_1 = {}
        branch_extracted_1['name'] = 'b-e-1'
        branch_extracted_1['hash'] = '0000400004000040000400004000040000400004'

        branch_extracted_2 = {}
        branch_extracted_2['name'] = 'b-e-2'
        branch_extracted_2['hash'] = '0000500005000050000500005000050000500005'

        known_branches = [branch_known_1, branch_known_2]
        extracted_branches = [branch_extracted_1, branch_extracted_2]

        res = self.fetcher.get_merge_target_from_branch_list(branch_merge_target, extracted_branches, known_branches)

        self.assertEqual('b-k-2-5', res['name'])
        self.assertEqual('0000700007000070000700007000070000700007', res['hash'])

    def test_get_merge_target_from_branch_list_found_in_extracted(self):
        branch_merge_target = {}
        branch_merge_target['name'] = 'b-e-1'
        branch_merge_target['hash'] = '0000400004000040000400004000040000400004'

        branch_known_1 = {}
        branch_known_1['name'] = 'b-k-1'
        branch_known_1['hash'] = '0000200002000020000200002000020000200002'
        branch_known_1['merge_target'] = {}
        branch_known_1['merge_target']['name'] = 'b-k-1-5'
        branch_known_1['merge_target']['hash'] = '0000800008000080000800008000080000800008'

        branch_known_2 = {}
        branch_known_2['name'] = 'b-k-2'
        branch_known_2['hash'] = '0000300003000030000300003000030000300003'
        branch_known_2['merge_target'] = {}
        branch_known_2['merge_target']['name'] = 'b-k-2-5'
        branch_known_2['merge_target']['hash'] = '0000700007000070000700007000070000700007'

        branch_extracted_1 = {}
        branch_extracted_1['name'] = 'master'
        branch_extracted_1['hash'] = '0000900009000090000900009000090000900009'

        branch_extracted_2 = {}
        branch_extracted_2['name'] = 'b-e-2'
        branch_extracted_2['hash'] = '0000500005000050000500005000050000500005'

        known_branches = [branch_known_1, branch_known_2]
        extracted_branches = [branch_extracted_1, branch_extracted_2]

        res = self.fetcher.get_merge_target_from_branch_list(branch_merge_target, extracted_branches, known_branches)

        self.assertEqual('master', res['name'])
        self.assertEqual('0000900009000090000900009000090000900009', res['hash'])

    def test_get_merge_target_from_branch_list_found_in_itself(self):
        branch_merge_target = {}
        branch_merge_target['name'] = 'b-9'
        branch_merge_target['hash'] = '0000900009000090000900009000090000900009'

        branch_known_1 = {}
        branch_known_1['name'] = 'b-k-1'
        branch_known_1['hash'] = '0000200002000020000200002000020000200002'
        branch_known_1['merge_target'] = {}
        branch_known_1['merge_target']['name'] = 'b-k-1-5'
        branch_known_1['merge_target']['hash'] = '0000800008000080000800008000080000800008'

        branch_known_2 = {}
        branch_known_2['name'] = 'b-k-2'
        branch_known_2['hash'] = '0000300003000030000300003000030000300003'
        branch_known_2['merge_target'] = {}
        branch_known_2['merge_target']['name'] = 'b-k-2-5'
        branch_known_2['merge_target']['hash'] = '0000700007000070000700007000070000700007'

        branch_extracted_1 = {}
        branch_extracted_1['name'] = 'b-e-1'
        branch_extracted_1['hash'] = '0000400004000040000400004000040000400004'

        branch_extracted_2 = {}
        branch_extracted_2['name'] = 'b-e-2'
        branch_extracted_2['hash'] = '0000500005000050000500005000050000500005'

        known_branches = [branch_known_1, branch_known_2]
        extracted_branches = [branch_extracted_1, branch_extracted_2]

        res = self.fetcher.get_merge_target_from_branch_list(branch_merge_target, extracted_branches, known_branches)

        self.assertEqual('b-9', res['name'])
        self.assertEqual('0000900009000090000900009000090000900009', res['hash'])

    def test_get_fork_point(self):
        commit_1 = {}
        commit_1['hash'] = '0000300003000030000300003000030000300003'

        commit_2 = {}
        commit_2['hash'] = '0000200002000020000200002000020000200002'

        commit_3 = {}
        commit_3['hash'] = '0000100001000010000100001000010000100001'

        commit_4 = {}
        commit_4['hash'] = '0000000000000000000000000000000000000000'

        commit_5 = {}
        commit_5['hash'] = '0000400004000040000400004000040000400004'

        commit_6 = {}
        commit_6['hash'] = '0000100001000010000100001000010000100001'

        commit_7 = {}
        commit_7['hash'] = '0000000000000000000000000000000000000000'

        branch_1 = {}
        branch_1['commits'] = [commit_1, commit_2, commit_3, commit_4]

        branch_2 = {}
        branch_2['commits'] = [commit_5, commit_6, commit_7]

        res = self.fetcher.get_fork_point_between_branches(branch_1, branch_2)

        self.assertEqual('0000100001000010000100001000010000100001', res)

    def test_get_fork_point_not_found(self):
        commit_1 = {}
        commit_1['hash'] = '0000300003000030000300003000030000300003'

        commit_2 = {}
        commit_2['hash'] = '0000200002000020000200002000020000200002'

        commit_3 = {}
        commit_3['hash'] = '0000100001000010000100001000010000100001'

        commit_4 = {}
        commit_4['hash'] = '0000000000000000000000000000000000000000'

        commit_5 = {}
        commit_5['hash'] = '0000400004000040000400004000040000400004'

        commit_6 = {}
        commit_6['hash'] = '0000800008000080000800008000080000800008'

        commit_7 = {}
        commit_7['hash'] = '0000900009000090000900009000090000900009'

        branch_1 = {}
        branch_1['commits'] = [commit_1, commit_2, commit_3, commit_4]

        branch_2 = {}
        branch_2['commits'] = [commit_5, commit_6, commit_7]

        res = self.fetcher.get_fork_point_between_branches(branch_1, branch_2)

        self.assertEqual('', res)

    @mock.patch('app.service.strongholdworker.download.GitFetcher.subprocess')
    def test_commands_get_diff_between_commits(self, mock_subprocess):
        commit_1 = '0000100001000010000100001000010000100001'
        commit_2 = '0000200002000020000200002000020000200002'

        self.fetcher.create_tmp_folder_for_git_project(self.obj)
        reports = self.fetcher.commands_get_diff_between_commits(self.obj, commit_1, commit_2)
        mock_subprocess.check_call.assert_called_once(['git', 'diff', commit_1, commit_2])
        self.assertEqual(1, mock_subprocess.check_call.call_count)

        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC', 'project')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC', 'log')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC', 'log', 'git_clone_stdout.txt')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'gitfetcher', 'proj-28-0123ABC', 'log', 'git_clone_stderr.txt')))

        self.assertEqual(1, len(reports['commands']))

        self.assertEqual('OK', reports['commands'][0]['status'])
        self.assertEqual(['git', 'diff', commit_1, commit_2], reports['commands'][0]['command'])
        self.assertEqual('', reports['commands'][0]['error'])
        self.assertEqual('', reports['commands'][0]['out'])

    def test_extract_diff_from_report(self):
        report1 = {}
        report1['status'] = 'OK'
        report1['command'] = ['git', 'rev-parse', 'master']
        report1['out'] = '0000100001000010000100001000010000100001'
        report1['error'] = ''

        report2 = {}
        report2['status'] = 'OK'
        report2['command'] = ['git', 'diff', '...']
        report2['out'] = 'diff-long-long-text'
        report2['error'] = ''

        obj = {}
        obj['status'] = True
        obj['commands'] = []
        obj['commands'].append(report1)
        obj['commands'].append(report2)

        diff = self.fetcher.extract_diff_from_report(obj)

        self.assertEqual('diff-long-long-text', diff)
