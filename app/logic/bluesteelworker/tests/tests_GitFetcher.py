""" Git Fetch tests """

from django.test import TestCase
from django.conf import settings
from django.utils import timezone
from django.utils.six import StringIO
from app.logic.bluesteelworker.download.GitFetcher import GitFetcher
from app.logic.bluesteelworker.download.ProjectFolderManager import ProjectFolderManager
from datetime import timedelta
import logging as log
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

        self.obj1 = {}
        self.obj1['git'] = {}
        self.obj1['git']['project'] = {}
        self.obj1['git']['project']['current_working_directory'] = self.tmp_folder
        self.obj1['git']['project']['tmp_directory'] = ['tmp-gitfetcher-folder']
        self.obj1['git']['project']['archive'] = 'archive-28-0123ABC'
        self.obj1['git']['project']['name'] = 'test-repo-1'
        self.obj1['git']['project']['git_project_search_path'] = 'test-repo-git-2'
        self.obj1['git']['project']['url'] = 'git-url'
        self.obj1['git']['branches'] = []
        self.obj1['git']['clone'] = {}
        self.obj1['git']['clone']['commands'] = []
        self.obj1['git']['clone']['commands'].append(['git','clone','https://llorensmarti@bitbucket.org/llorensmarti/test-repo.git'])
        self.obj1['git']['clone']['commands'].append(['git','submodule','update', '--init', '--recursive'])
        self.obj1['git']['fetch'] = {}
        self.obj1['git']['fetch']['commands'] = []
        self.obj1['git']['fetch']['commands'].append(['git', 'reset', '--hard', 'origin/master'])
        self.obj1['git']['fetch']['commands'].append(['git', 'clean', '-f', '-d', '-q'])
        self.obj1['git']['fetch']['commands'].append(['git', 'pull', '-r', 'origin', 'master'])
        self.obj1['git']['fetch']['commands'].append(['git', 'checkout', 'master'])
        self.obj1['git']['fetch']['commands'].append(['git', 'submodule', 'update', '--init', '--recursive'])

        self.obj2 = {}
        self.obj2['git'] = {}
        self.obj2['git']['project'] = {}
        self.obj2['git']['project']['current_working_directory'] = self.tmp_folder
        self.obj2['git']['project']['tmp_directory'] = ['tmp-gitfetcher-folder']
        self.obj2['git']['project']['archive'] = 'archive-28-0123ABC'
        self.obj2['git']['project']['name'] = 'test-repo-2'
        self.obj2['git']['project']['git_project_search_path'] = 'test-repo-git-2'
        self.obj2['git']['project']['url'] = 'git-url'
        self.obj2['git']['branches'] = []
        self.obj2['git']['clone'] = {}
        self.obj2['git']['clone']['commands'] = []
        self.obj2['git']['clone']['commands'].append(['git','clone','https://llorensmarti@bitbucket.org/llorensmarti/test-repo.git'])
        self.obj2['git']['clone']['commands'].append(['git','submodule','update', '--init', '--recursive'])
        self.obj2['git']['fetch'] = {}
        self.obj2['git']['fetch']['commands'] = []
        self.obj2['git']['fetch']['commands'].append(['git', 'reset', '--hard', 'origin/master'])
        self.obj2['git']['fetch']['commands'].append(['git', 'clean', '-f', '-d', '-q'])
        self.obj2['git']['fetch']['commands'].append(['git', 'pull', '-r', 'origin', 'master'])
        self.obj2['git']['fetch']['commands'].append(['git', 'checkout', 'master'])
        self.obj2['git']['fetch']['commands'].append(['git', 'submodule', 'update', '--init', '--recursive'])

        self.fetcher = GitFetcher(log.ERROR)

    def tearDown(self):
        if os.path.exists(self.tmp_folder):
            shutil.rmtree(self.tmp_folder)

    def create_git_hidden_folder(self, root, tmp, archive, name_project):
        path1 = os.path.join(root, tmp, archive, name_project, 'project', name_project, 'test-repo-git-1','.git')
        path2 = os.path.join(root, tmp, archive, name_project, 'project', name_project, 'test-repo-git-2','.git')
        path3 = os.path.join(root, tmp, archive, name_project, 'project', name_project, 'test-repo-git-3','.git')
        os.makedirs(path1)
        os.makedirs(path2)
        os.makedirs(path3)

    def create_paths(self, obj):
        paths = ProjectFolderManager.get_folder_paths(
            obj['git']['project']['current_working_directory'],
            obj['git']['project']['tmp_directory'],
            obj['git']['project']['archive'],
            obj['git']['project']['name'],
            obj['git']['project']['git_project_search_path']
        )

        ProjectFolderManager.create_tmp_folder_for_git_project(paths)
        os.makedirs(os.path.join(paths['project'], 'test-repo-git-1/.git'))
        os.makedirs(os.path.join(paths['project'], 'test-repo-git-2/.git'))
        os.makedirs(os.path.join(paths['project'], 'test-repo-git-3/.git'))
        return paths

    def test_find_first_git_project_inside_project_path(self):
        self.create_paths(self.obj1)
        paths = GitFetcher.get_project_paths(self.obj1)
        found_path = GitFetcher.get_first_git_project_found_path(paths)

        self.assertEqual(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1', 'project', 'test-repo-git-2'), found_path)

    @mock.patch('app.logic.bluesteelworker.download.CommandExecutioner.subprocess.call')
    def test_clone_project(self, mock_subprocess):
        mock_subprocess.return_value = 0
        self.create_paths(self.obj1)
        reports = self.fetcher.commands_clone_git_project(self.obj1)

        name, args, side = mock_subprocess.mock_calls[0]
        self.assertEqual(['git', 'clone', 'https://llorensmarti@bitbucket.org/llorensmarti/test-repo.git'], args[0])

        name, args, side = mock_subprocess.mock_calls[1]
        self.assertEqual(['git', 'submodule', 'update', '--init', '--recursive'], args[0])

        self.assertEqual(2, mock_subprocess.call_count)

        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1', 'project')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1', 'log')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1', 'log', 'out.txt')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1', 'log', 'err.txt')))

        self.assertEqual(2, len(reports['commands']))

        self.assertEqual(0, reports['commands'][0]['result']['status'])
        self.assertEqual('git clone https://llorensmarti@bitbucket.org/llorensmarti/test-repo.git', reports['commands'][0]['command'])
        self.assertEqual('', reports['commands'][0]['result']['error'])
        self.assertEqual('', reports['commands'][0]['result']['out'])

        self.assertEqual(0, reports['commands'][1]['result']['status'])
        self.assertEqual('git submodule update --init --recursive', reports['commands'][1]['command'])
        self.assertEqual('', reports['commands'][1]['result']['error'])
        self.assertEqual('', reports['commands'][1]['result']['out'])


    @mock.patch('app.logic.bluesteelworker.download.CommandExecutioner.subprocess.call')
    def test_fetch_project(self, mock_subprocess):
        mock_subprocess.return_value = 0
        self.create_paths(self.obj1)
        self.create_git_hidden_folder(settings.TMP_ROOT, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1')
        reports = self.fetcher.commands_fetch_git_project(self.obj1)

        name, args, side = mock_subprocess.mock_calls[0]
        self.assertEqual(['git', 'reset', '--hard', 'origin/master'], args[0])

        name, args, side = mock_subprocess.mock_calls[1]
        self.assertEqual(['git', 'clean', '-f', '-d', '-q'], args[0])

        name, args, side = mock_subprocess.mock_calls[2]
        self.assertEqual(['git', 'pull', '-r', 'origin', 'master'], args[0])

        name, args, side = mock_subprocess.mock_calls[3]
        self.assertEqual(['git', 'checkout', 'master'], args[0])

        name, args, side = mock_subprocess.mock_calls[4]
        self.assertEqual(['git', 'submodule', 'update', '--init', '--recursive'], args[0])

        self.assertEqual(5, mock_subprocess.call_count)

        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1', 'project')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1', 'log')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1', 'log', 'out.txt')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1', 'log', 'err.txt')))

        self.assertEqual(5, len(reports['commands']))

        self.assertEqual(0, reports['commands'][0]['result']['status'])
        self.assertEqual('git reset --hard origin/master', reports['commands'][0]['command'])
        self.assertEqual('', reports['commands'][0]['result']['error'])
        self.assertEqual('', reports['commands'][0]['result']['out'])

        self.assertEqual(0, reports['commands'][1]['result']['status'])
        self.assertEqual('git clean -f -d -q', reports['commands'][1]['command'])
        self.assertEqual('', reports['commands'][1]['result']['error'])
        self.assertEqual('', reports['commands'][1]['result']['out'])

        self.assertEqual(0, reports['commands'][2]['result']['status'])
        self.assertEqual('git pull -r origin master', reports['commands'][2]['command'])
        self.assertEqual('', reports['commands'][2]['result']['error'])
        self.assertEqual('', reports['commands'][2]['result']['out'])

        self.assertEqual(0, reports['commands'][3]['result']['status'])
        self.assertEqual('git checkout master', reports['commands'][3]['command'])
        self.assertEqual('', reports['commands'][3]['result']['error'])
        self.assertEqual('', reports['commands'][3]['result']['out'])

        self.assertEqual(0, reports['commands'][4]['result']['status'])
        self.assertEqual('git submodule update --init --recursive', reports['commands'][4]['command'])
        self.assertEqual('', reports['commands'][4]['result']['error'])
        self.assertEqual('', reports['commands'][4]['result']['out'])

    @mock.patch('app.logic.bluesteelworker.download.CommandExecutioner.subprocess.call')
    def test_fetch_project_with_incorrect_git_project_search_path(self, mock_subprocess):
        mock_subprocess.return_value = 0
        self.create_paths(self.obj1)
        self.create_git_hidden_folder(settings.TMP_ROOT, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1')
        self.obj1['git']['project']['git_project_search_path'] = 'this-folder-does-not-exists'
        reports = self.fetcher.commands_fetch_git_project(self.obj1)

        self.assertEqual(1, len(reports['commands']))

        self.assertEqual(-1, reports['commands'][0]['result']['status'])
        self.assertEqual('git_project_search_path', reports['commands'][0]['command'])
        self.assertTrue('tmp/test/tmp-gitfetcher-folder/archive-28-0123ABC/test-repo-1/project/this-folder-does-not-exists \nProject current working directory not found' in reports['commands'][0]['result']['error'])
        self.assertEqual('', reports['commands'][0]['result']['out'])

    @mock.patch('app.logic.bluesteelworker.download.CommandExecutioner.subprocess.call')
    def test_get_branch_names(self, mock_subprocess):
        mock_subprocess.return_value = 0
        self.create_paths(self.obj1)
        self.create_git_hidden_folder(settings.TMP_ROOT, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1')
        reports = self.fetcher.commands_get_branch_names(self.obj1, ['git', 'branch'])

        name, args, side = mock_subprocess.mock_calls[0]
        self.assertEqual(['git', 'branch'], args[0])

        self.assertEqual(1, mock_subprocess.call_count)

        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1', 'project')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1', 'log')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1', 'log', 'out.txt')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1', 'log', 'err.txt')))

        self.assertEqual(1, len(reports['commands']))

        self.assertEqual(0, reports['commands'][0]['result']['status'])
        self.assertEqual('git branch', reports['commands'][0]['command'])
        self.assertEqual('', reports['commands'][0]['result']['error'])
        self.assertEqual('', reports['commands'][0]['result']['out'])

    @mock.patch('app.logic.bluesteelworker.download.CommandExecutioner.subprocess.call')
    def test_get_branch_names(self, mock_subprocess):
        mock_subprocess.return_value = 0
        self.create_paths(self.obj1)
        self.create_git_hidden_folder(settings.TMP_ROOT, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1')
        reports = self.fetcher.commands_remove_branches(self.obj1, ['b-name-1', 'b-name-2', 'b-name-3'])

        name, args, side = mock_subprocess.mock_calls[0]
        self.assertEqual(['git', 'branch', '-D', 'b-name-1'], args[0])

        name, args, side = mock_subprocess.mock_calls[1]
        self.assertEqual(['git', 'branch', '-D', 'b-name-2'], args[0])

        name, args, side = mock_subprocess.mock_calls[2]
        self.assertEqual(['git', 'branch', '-D', 'b-name-3'], args[0])

        self.assertEqual(3, mock_subprocess.call_count)

        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1', 'project')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1', 'log')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1', 'log', 'out.txt')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1', 'log', 'err.txt')))

        self.assertEqual(3, len(reports['commands']))

        self.assertEqual(0, reports['commands'][0]['result']['status'])
        self.assertEqual('git branch -D b-name-1', reports['commands'][0]['command'])
        self.assertEqual('', reports['commands'][0]['result']['error'])
        self.assertEqual('', reports['commands'][0]['result']['out'])

        self.assertEqual(0, reports['commands'][1]['result']['status'])
        self.assertEqual('git branch -D b-name-2', reports['commands'][1]['command'])
        self.assertEqual('', reports['commands'][1]['result']['error'])
        self.assertEqual('', reports['commands'][1]['result']['out'])

        self.assertEqual(0, reports['commands'][2]['result']['status'])
        self.assertEqual('git branch -D b-name-3', reports['commands'][2]['command'])
        self.assertEqual('', reports['commands'][2]['result']['error'])
        self.assertEqual('', reports['commands'][2]['result']['out'])

    def test_extract_remote_branch_names_from_reports(self):
        # {'commands': [{'command': u'git branch -r', 'result': {'status': 0, 'finish_time': '2016-02-04T06:54:18.163479', 'start_time': '2016-02-04T06:54:18.157050', 'error': '', 'out': '  origin/HEAD -> origin/master\n  origin/branch-1\n  origin/branch-2\n  origin/branch-test-1\n  origin/master\n'}}]}

        report1 = {}
        report1['command'] = 'git branch -r'
        report1['result'] = {}
        report1['result']['status'] = 0
        report1['result']['out'] = '  origin/HEAD -> origin/master\n  origin/branch-1\n  origin/branch-2\n  origin/branch-test-1\n  origin/master\n'
        report1['result']['error'] = ''

        obj = {}
        obj['status'] = True
        obj['commands'] = []
        obj['commands'].append(report1)

        branch_names = self.fetcher.extract_remote_branch_names_from_reports(obj)

        self.assertEqual(4, len(branch_names))
        self.assertEqual('origin/branch-1', branch_names[0])
        self.assertEqual('origin/branch-2', branch_names[1])
        self.assertEqual('origin/branch-test-1', branch_names[2])
        self.assertEqual('origin/master', branch_names[3])

    def test_extract_local_branch_names_from_reports(self):
        report1 = {}
        report1['command'] = 'git branch -r'
        report1['result'] = {}
        report1['result']['status'] = 0
        report1['result']['out'] = '  * master\n  branch-1\n  branch-2\n  branch-test-1\n'
        report1['result']['error'] = ''

        obj = {}
        obj['status'] = True
        obj['commands'] = []
        obj['commands'].append(report1)

        branch_names = self.fetcher.extract_remote_branch_names_from_reports(obj)

        self.assertEqual(4, len(branch_names))
        self.assertEqual('master', branch_names[0])
        self.assertEqual('branch-1', branch_names[1])
        self.assertEqual('branch-2', branch_names[2])
        self.assertEqual('branch-test-1', branch_names[3])

    def test_extract_branch_names_correct(self):
        report1 = {}
        report1['command'] = 'git branch'
        report1['result'] = {}
        report1['result']['status'] = 0
        report1['result']['out'] = ' * master\n branch-1\n\n'
        report1['result']['error'] = ''

        report2 = {}
        report2['command'] = 'git status'
        report2['result'] = {}
        report2['result']['status'] = 0
        report2['result']['out'] = 'Hey!!!'
        report2['result']['error'] = ''

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
        report1['command'] = 'git branch'
        report1['result'] = {}
        report1['result']['status'] = 1
        report1['result']['out'] = ''
        report1['result']['error'] = 'Some error'

        obj = {}
        obj['status'] = False
        obj['commands'] = []
        obj['commands'].append(report1)

        branch_names = self.fetcher.extract_branch_names_from_report(obj)

        self.assertEqual(0, len(branch_names))

    @mock.patch('app.logic.bluesteelworker.download.CommandExecutioner.subprocess.call')
    def test_checkout_remote_branches_to_local(self, mock_subprocess):
        branch_names = ['origin/master', 'origin/branch-1', 'origin/branch-2', 'origin/branch-test-1']
        mock_subprocess.return_value = 0
        self.create_paths(self.obj1)
        self.create_git_hidden_folder(settings.TMP_ROOT, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1')

        reports = self.fetcher.checkout_remote_branches_to_local(self.obj1, branch_names)

        name, args, side = mock_subprocess.mock_calls[0]
        self.assertEqual(['git', 'checkout', 'master'], args[0])

        name, args, side = mock_subprocess.mock_calls[1]
        self.assertEqual(['git', 'checkout', 'branch-1'], args[0])

        name, args, side = mock_subprocess.mock_calls[2]
        self.assertEqual(['git', 'checkout', 'branch-2'], args[0])

        name, args, side = mock_subprocess.mock_calls[3]
        self.assertEqual(['git', 'checkout', 'branch-test-1'], args[0])

        self.assertEqual(4, mock_subprocess.call_count)

        self.assertEqual(4, len(reports['commands']))

        self.assertEqual(0, reports['commands'][0]['result']['status'])
        self.assertEqual('git checkout master', reports['commands'][0]['command'])
        self.assertEqual('', reports['commands'][0]['result']['error'])
        self.assertEqual('', reports['commands'][0]['result']['out'])

        self.assertEqual(0, reports['commands'][1]['result']['status'])
        self.assertEqual('git checkout branch-1', reports['commands'][1]['command'])
        self.assertEqual('', reports['commands'][1]['result']['error'])
        self.assertEqual('', reports['commands'][1]['result']['out'])

        self.assertEqual(0, reports['commands'][2]['result']['status'])
        self.assertEqual('git checkout branch-2', reports['commands'][2]['command'])
        self.assertEqual('', reports['commands'][2]['result']['error'])
        self.assertEqual('', reports['commands'][2]['result']['out'])

        self.assertEqual(0, reports['commands'][3]['result']['status'])
        self.assertEqual('git checkout branch-test-1', reports['commands'][3]['command'])
        self.assertEqual('', reports['commands'][3]['result']['error'])
        self.assertEqual('', reports['commands'][3]['result']['out'])


    @mock.patch('app.logic.bluesteelworker.download.CommandExecutioner.subprocess.call')
    def test_commands_get_branch_names_and_hashes(self, mock_subprocess):
        branch_names = ['master', 'branch-1', 'branch-2']
        mock_subprocess.return_value = 0
        self.create_paths(self.obj1)
        self.create_git_hidden_folder(settings.TMP_ROOT, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1')
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC','test-repo-1', 'project', 'test-repo-1', 'test-repo-git-2', '.git')))

        reports = self.fetcher.commands_get_branch_names_and_hashes(self.obj1, branch_names)

        name, args, side = mock_subprocess.mock_calls[0]
        self.assertEqual(['git', 'rev-parse', 'master'], args[0])

        name, args, side = mock_subprocess.mock_calls[1]
        self.assertEqual(['git', 'rev-parse', 'branch-1'], args[0])

        name, args, side = mock_subprocess.mock_calls[2]
        self.assertEqual(['git', 'rev-parse', 'branch-2'], args[0])

        self.assertEqual(3, mock_subprocess.call_count)

        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC','test-repo-1')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC','test-repo-1', 'project')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC','test-repo-1', 'project', 'test-repo-git-1')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC','test-repo-1', 'project', 'test-repo-git-2')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC','test-repo-1', 'project', 'test-repo-git-3')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC','test-repo-1', 'log')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC','test-repo-1', 'log', 'out.txt')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC','test-repo-1', 'log', 'err.txt')))

        self.assertEqual(3, len(reports['commands']))

        self.assertEqual(0, reports['commands'][0]['result']['status'])
        self.assertEqual('git rev-parse master', reports['commands'][0]['command'])
        self.assertEqual('', reports['commands'][0]['result']['error'])
        self.assertEqual('', reports['commands'][0]['result']['out'])

        self.assertEqual(0, reports['commands'][1]['result']['status'])
        self.assertEqual('git rev-parse branch-1', reports['commands'][1]['command'])
        self.assertEqual('', reports['commands'][1]['result']['error'])
        self.assertEqual('', reports['commands'][1]['result']['out'])

        self.assertEqual(0, reports['commands'][2]['result']['status'])
        self.assertEqual('git rev-parse branch-2', reports['commands'][2]['command'])
        self.assertEqual('', reports['commands'][2]['result']['error'])
        self.assertEqual('', reports['commands'][2]['result']['out'])

    def test_extract_branch_names_and_hashes_correct(self):
        report1 = {}
        report1['command'] = 'git rev-parse master'
        report1['result'] = {}
        report1['result']['status'] = 0
        report1['result']['out'] = '0000100001000010000100001000010000100001'
        report1['result']['error'] = ''

        report2 = {}
        report2['command'] = 'git rev-parse branch-1'
        report2['result'] = {}
        report2['result']['status'] = 0
        report2['result']['out'] = '0000200002000020000200002000020000200002'
        report2['result']['error'] = ''

        obj = {}
        obj['status'] = True
        obj['commands'] = []
        obj['commands'].append(report1)
        obj['commands'].append(report2)

        branch_names = self.fetcher.extract_branch_names_hashes_from_report(obj)

        self.assertEqual(2, len(branch_names))
        self.assertEqual('master', branch_names[0]['name'])
        self.assertEqual('0000100001000010000100001000010000100001', branch_names[0]['commit_hash'])
        self.assertEqual('branch-1', branch_names[1]['name'])
        self.assertEqual('0000200002000020000200002000020000200002', branch_names[1]['commit_hash'])

    @mock.patch('app.logic.bluesteelworker.download.CommandExecutioner.subprocess.call')
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

        mock_subprocess.return_value = 0
        self.create_paths(self.obj1)
        self.create_git_hidden_folder(settings.TMP_ROOT, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1')
        reports = self.fetcher.commands_get_commits_from_branch(self.obj1, branch_name)

        name, args, side = mock_subprocess.mock_calls[0]
        self.assertEqual(['git', 'reset', '--hard'], args[0])

        name, args, side = mock_subprocess.mock_calls[1]
        self.assertEqual(['git', 'clean', '-f', '-d', '-q'], args[0])

        name, args, side = mock_subprocess.mock_calls[2]
        self.assertEqual(['git', 'checkout', 'branch-1'], args[0])

        name, args, side = mock_subprocess.mock_calls[3]
        self.assertEqual(['git', 'submodule', 'update', '--init', '--recursive'], args[0])

        name, args, side = mock_subprocess.mock_calls[4]
        self.assertEqual(['git', 'pull', '-r'], args[0])

        name, args, side = mock_subprocess.mock_calls[5]
        self.assertEqual(['git', 'log', '--first-parent', '--date=iso', pretty_string], args[0])

        self.assertEqual(6, mock_subprocess.call_count)

        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC','test-repo-1')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC','test-repo-1', 'project')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC','test-repo-1', 'log')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC','test-repo-1', 'log', 'out.txt')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC','test-repo-1', 'log', 'err.txt')))

        self.assertEqual(6, len(reports['commands']))

        self.assertEqual(0, reports['commands'][0]['result']['status'])
        self.assertEqual('git reset --hard', reports['commands'][0]['command'])
        self.assertEqual('', reports['commands'][0]['result']['error'])
        self.assertEqual('', reports['commands'][0]['result']['out'])

        self.assertEqual(0, reports['commands'][1]['result']['status'])
        self.assertEqual('git clean -f -d -q', reports['commands'][1]['command'])
        self.assertEqual('', reports['commands'][1]['result']['error'])
        self.assertEqual('', reports['commands'][1]['result']['out'])

        self.assertEqual(0, reports['commands'][2]['result']['status'])
        self.assertEqual('git checkout branch-1', reports['commands'][2]['command'])
        self.assertEqual('', reports['commands'][2]['result']['error'])
        self.assertEqual('', reports['commands'][2]['result']['out'])

        self.assertEqual(0, reports['commands'][3]['result']['status'])
        self.assertEqual('git submodule update --init --recursive', reports['commands'][3]['command'])
        self.assertEqual('', reports['commands'][3]['result']['error'])
        self.assertEqual('', reports['commands'][3]['result']['out'])

        self.assertEqual(0, reports['commands'][4]['result']['status'])
        self.assertEqual('git pull -r', reports['commands'][4]['command'])
        self.assertEqual('', reports['commands'][4]['result']['error'])
        self.assertEqual('', reports['commands'][4]['result']['out'])

        self.assertEqual(0, reports['commands'][5]['result']['status'])
        self.assertEqual('git log --first-parent --date=iso {0}'.format(pretty_string), reports['commands'][5]['command'])
        self.assertEqual('', reports['commands'][5]['result']['error'])
        self.assertEqual('', reports['commands'][5]['result']['out'])

    def test_extract_and_format_commits_from_report(self):
        report1 = {}
        report1['command'] = 'git rev-parse master'
        report1['result'] = {}
        report1['result']['status'] = 0
        report1['result']['out'] = '0000100001000010000100001000010000100001'
        report1['result']['error'] = ''

        report2 = {}
        report2['command'] = 'git log ...'
        report2['result'] = {}
        report2['result']['status'] = 0
        report2['result']['out'] = '{\
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
        report2['result']['error'] = ''

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

    def test_extract_and_format_commits_from_report_with_wrong_escape_chars(self):
        report1 = {}
        report1['command'] = 'git log ...'
        report1['result'] = {}
        report1['result']['status'] = 0
        report1['result']['out'] = '{\
                "hash":"0000100001000010000100001000010000100001",\
                "parent_hashes":"0000500005000050000500005000050000500005 0000200002000020000200002000020000200002",\
                "author": {\
                    "name":"llorensmarti",\
                    "email":"lgarcia@test.com",\
                    "date":"2015-03-08T23:13:33-07:00"\
                },\
                "committer": {\
                    "name":"llorens\marti2",\
                    "email":"lgarcia-2@test.com",\
                    "date":"2015-03-08T23:13:33-07:00"\
                }\
            },'
        report1['result']['error'] = ''

        obj = {}
        obj['status'] = True
        obj['commands'] = []
        obj['commands'].append(report1)

        commits = self.fetcher.extract_and_format_commits_from_report(obj)

        self.assertEqual(1, len(commits))

        self.assertEqual('0000100001000010000100001000010000100001', commits[0]['hash'])
        self.assertEqual(2, len(commits[0]['parent_hashes']))
        self.assertEqual('0000500005000050000500005000050000500005', commits[0]['parent_hashes'][0])
        self.assertEqual('0000200002000020000200002000020000200002', commits[0]['parent_hashes'][1])
        self.assertEqual('llorensmarti', commits[0]['author']['name'])
        self.assertEqual('lgarcia@test.com', commits[0]['author']['email'])
        self.assertEqual('2015-03-08T23:13:33-07:00', commits[0]['author']['date'])
        self.assertEqual('llorens\marti2', commits[0]['committer']['name'])
        self.assertEqual('lgarcia-2@test.com', commits[0]['committer']['email'])
        self.assertEqual('2015-03-08T23:13:33-07:00', commits[0]['committer']['date'])

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
        branch1['commit_hash'] = '0000700007000070000700007000070000700007'
        branch1['merge_target'] = {}
        branch1['merge_target']['current_branch'] = {}
        branch1['merge_target']['current_branch']['name'] = 'name-1'
        branch1['merge_target']['current_branch']['commit_hash'] = '0000700007000070000700007000070000700007'
        branch1['merge_target']['target_branch'] = {}
        branch1['merge_target']['target_branch']['name'] = 'name-1'
        branch1['merge_target']['target_branch']['commit_hash'] = '0000700007000070000700007000070000700007'

        branch2 = {}
        branch2['name'] = 'name-1'
        branch2['commit_hash'] = '0000800008000080000800008000080000800008'
        branch2['merge_target'] = {}
        branch2['merge_target']['current_branch'] = {}
        branch2['merge_target']['current_branch']['name'] = 'name-2'
        branch2['merge_target']['current_branch']['commit_hash'] = '0000800008000080000800008000080000800008'
        branch2['merge_target']['target_branch'] = {}
        branch2['merge_target']['target_branch']['name'] = 'name-1'
        branch2['merge_target']['target_branch']['commit_hash'] = '0000700007000070000700007000070000700007'

        branch3 = {}
        branch3['name'] = 'name-3'
        branch3['commit_hash'] = '0000900009000090000900009000090000900009'
        branch3['merge_target'] = {}
        branch3['merge_target']['current_branch'] = {}
        branch3['merge_target']['current_branch']['name'] = 'name-3'
        branch3['merge_target']['current_branch']['commit_hash'] = '0000900009000090000900009000090000900009'
        branch3['merge_target']['target_branch'] = {}
        branch3['merge_target']['target_branch']['name'] = 'name-1'
        branch3['merge_target']['target_branch']['commit_hash'] = '0000700007000070000700007000070000700007'

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
        branch1['commit_hash'] = '0000700007000070000700007000070000700007'
        branch1['merge_target'] = {}
        branch1['merge_target']['current_branch'] = {}
        branch1['merge_target']['current_branch']['name'] = 'name-1'
        branch1['merge_target']['current_branch']['commit_hash'] = '0000700007000070000700007000070000700007'
        branch1['merge_target']['target_branch'] = {}
        branch1['merge_target']['target_branch']['name'] = 'name-1'
        branch1['merge_target']['target_branch']['commit_hash'] = '0000700007000070000700007000070000700007'

        branch2 = {}
        branch2['name'] = 'name-2'
        branch2['commit_hash'] = '0000800008000080000800008000080000800008'
        branch2['merge_target'] = {}
        branch2['merge_target']['current_branch'] = {}
        branch2['merge_target']['current_branch']['name'] = 'name-2'
        branch2['merge_target']['current_branch']['commit_hash'] = '0000800008000080000800008000080000800008'
        branch2['merge_target']['target_branch'] = {}
        branch2['merge_target']['target_branch']['name'] = 'name-1'
        branch2['merge_target']['target_branch']['commit_hash'] = '0000700007000070000700007000070000700007'

        branch3 = {}
        branch3['name'] = 'name-3'
        branch3['commit_hash'] = '0000200002000020000200002000020000200002'
        branch3['merge_target'] = {}
        branch3['merge_target']['current_branch'] = {}
        branch3['merge_target']['current_branch']['name'] = 'name-3'
        branch3['merge_target']['current_branch']['commit_hash'] = '0000200002000020000200002000020000200002'
        branch3['merge_target']['target_branch'] = {}
        branch3['merge_target']['target_branch']['name'] = 'name-1'
        branch3['merge_target']['target_branch']['commit_hash'] = '0000700007000070000700007000070000700007'

        known_branches = []
        known_branches.append(branch1)
        known_branches.append(branch2)
        known_branches.append(branch3)

        res = self.fetcher.trim_commit_list_with_known_branches(commits, known_branches)

        self.assertEqual(2, len(res))
        self.assertEqual('0000100001000010000100001000010000100001', res[0]['hash'])
        self.assertEqual('0000200002000020000200002000020000200002', res[1]['hash'])

    @mock.patch('app.logic.bluesteelworker.download.CommandExecutioner.subprocess.call')
    def test_commands_get_shared_commit_between_branches(self, mock_subprocess):
        branch1 = {}
        branch1['name'] = 'branch-1'
        branch1['commit_hash'] = '0000100001000010000100001000010000100001'

        branch2 = {}
        branch2['name'] = 'branch-2'
        branch2['commit_hash'] = '0000200002000020000200002000020000200002'

        mock_subprocess.return_value = 0
        self.create_paths(self.obj1)
        self.create_git_hidden_folder(settings.TMP_ROOT, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1')
        reports = self.fetcher.commands_get_fork_commit_between_branches(self.obj1, branch1, branch2)

        name, args, side = mock_subprocess.mock_calls[0]
        self.assertEqual(['git', 'merge-base', branch1['commit_hash'], branch2['commit_hash']], args[0])

        self.assertEqual(1, mock_subprocess.call_count)

        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1', 'project')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1', 'log')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1', 'log', 'out.txt')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1', 'log', 'err.txt')))

        self.assertEqual(1, len(reports['commands']))

        self.assertEqual(0, reports['commands'][0]['result']['status'])
        self.assertEqual('git merge-base {0} {1}'.format(branch1['commit_hash'], branch2['commit_hash']), reports['commands'][0]['command'])
        self.assertEqual('', reports['commands'][0]['result']['error'])
        self.assertEqual('', reports['commands'][0]['result']['out'])

    def test_get_merge_target_from_branch_list_found_in_known(self):
        branch_merge_target = {}
        branch_merge_target['name'] = 'b-k-2'
        branch_merge_target['commit_hash'] = '0000300003000030000300003000030000300003'

        branch_known_1 = {}
        branch_known_1['name'] = 'b-k-1'
        branch_known_1['commit_hash'] = '0000200002000020000200002000020000200002'
        branch_known_1['merge_target'] = {}
        branch_known_1['merge_target']['current_branch'] = {}
        branch_known_1['merge_target']['current_branch']['name'] = 'b-k-1'
        branch_known_1['merge_target']['current_branch']['commit_hash'] = '0000200002000020000200002000020000200002'
        branch_known_1['merge_target']['target_branch'] = {}
        branch_known_1['merge_target']['target_branch']['name'] = 'b-k-1-5'
        branch_known_1['merge_target']['target_branch']['commit_hash'] = '0000800008000080000800008000080000800008'

        branch_known_2 = {}
        branch_known_2['name'] = 'b-k-2'
        branch_known_2['commit_hash'] = '0000300003000030000300003000030000300003'
        branch_known_2['merge_target'] = {}
        branch_known_2['merge_target']['current_branch'] = {}
        branch_known_2['merge_target']['current_branch']['name'] = 'b-k-2'
        branch_known_2['merge_target']['current_branch']['commit_hash'] = '0000300003000030000300003000030000300003'
        branch_known_2['merge_target']['target_branch'] = {}
        branch_known_2['merge_target']['target_branch']['name'] = 'b-k-2-5'
        branch_known_2['merge_target']['target_branch']['commit_hash'] = '0000700007000070000700007000070000700007'

        branch_extracted_1 = {}
        branch_extracted_1['name'] = 'b-e-1'
        branch_extracted_1['commit_hash'] = '0000400004000040000400004000040000400004'

        branch_extracted_2 = {}
        branch_extracted_2['name'] = 'b-e-2'
        branch_extracted_2['commit_hash'] = '0000500005000050000500005000050000500005'

        branch_extracted_3 = {}
        branch_extracted_3['name'] = 'b-k-2-5'
        branch_extracted_3['commit_hash'] = '0000700007000070000700007000070000700007'

        known_branches = [branch_known_1, branch_known_2]
        extracted_branches = [branch_extracted_1, branch_extracted_2, branch_extracted_3]

        res = self.fetcher.get_merge_target_from_branch_list(branch_merge_target, extracted_branches, known_branches)

        self.assertEqual('b-k-2', res['current_branch']['name'])
        self.assertEqual('0000300003000030000300003000030000300003', res['current_branch']['commit_hash'])
        self.assertEqual('b-k-2-5', res['target_branch']['name'])
        self.assertEqual('0000700007000070000700007000070000700007', res['target_branch']['commit_hash'])

    def test_get_merge_target_from_branch_list_found_in_known_but_keep_latest_commit(self):
        branch_merge_target = {}
        branch_merge_target['name'] = 'b-k-1'
        branch_merge_target['commit_hash'] = '0000300003000030000300003000030000300003'

        branch_known_1 = {}
        branch_known_1['name'] = 'master'
        branch_known_1['commit_hash'] = '0000200002000020000200002000020000200002'
        branch_known_1['merge_target'] = {}
        branch_known_1['merge_target']['current_branch'] = {}
        branch_known_1['merge_target']['current_branch']['name'] = 'master'
        branch_known_1['merge_target']['current_branch']['commit_hash'] = '0000200002000020000200002000020000200002'
        branch_known_1['merge_target']['target_branch'] = {}
        branch_known_1['merge_target']['target_branch']['name'] = 'master'
        branch_known_1['merge_target']['target_branch']['commit_hash'] = '0000200002000020000200002000020000200002'

        branch_known_2 = {}
        branch_known_2['name'] = 'b-k-1'
        branch_known_2['commit_hash'] = '0000300003000030000300003000030000300003'
        branch_known_2['merge_target'] = {}
        branch_known_2['merge_target']['current_branch'] = {}
        branch_known_2['merge_target']['current_branch']['name'] = 'b-k-1'
        branch_known_2['merge_target']['current_branch']['commit_hash'] = '0000300003000030000300003000030000300003'
        branch_known_2['merge_target']['target_branch'] = {}
        branch_known_2['merge_target']['target_branch']['name'] = 'master'
        branch_known_2['merge_target']['target_branch']['commit_hash'] = '0000200002000020000200002000020000200002'

        branch_extracted_1 = {}
        branch_extracted_1['name'] = 'master'
        branch_extracted_1['commit_hash'] = '0000900009000090000900009000090000900009'

        branch_extracted_2 = {}
        branch_extracted_2['name'] = 'b-k-1'
        branch_extracted_2['comit_hash'] = '0000300003000030000300003000030000300003'

        known_branches = [branch_known_1, branch_known_2]
        extracted_branches = [branch_extracted_1, branch_extracted_2]

        res = self.fetcher.get_merge_target_from_branch_list(branch_merge_target, extracted_branches, known_branches)

        self.assertEqual('b-k-1', res['current_branch']['name'])
        self.assertEqual('0000300003000030000300003000030000300003', res['current_branch']['commit_hash'])
        self.assertEqual('master', res['target_branch']['name'])
        self.assertEqual('0000900009000090000900009000090000900009', res['target_branch']['commit_hash'])

    def test_get_merge_target_from_branch_list_found_in_extracted(self):
        branch_merge_target = {}
        branch_merge_target['name'] = 'b-e-1'
        branch_merge_target['commit_hash'] = '0000400004000040000400004000040000400004'

        branch_known_1 = {}
        branch_known_1['name'] = 'b-k-1'
        branch_known_1['commit_hash'] = '0000200002000020000200002000020000200002'
        branch_known_1['merge_target'] = {}
        branch_known_1['merge_target']['current_branch'] = {}
        branch_known_1['merge_target']['current_branch']['name'] = 'b-k-1'
        branch_known_1['merge_target']['current_branch']['commit_hash'] = '0000200002000020000200002000020000200002'
        branch_known_1['merge_target']['target_branch'] = {}
        branch_known_1['merge_target']['target_branch']['name'] = 'b-k-1-5'
        branch_known_1['merge_target']['target_branch']['commit_hash'] = '0000800008000080000800008000080000800008'

        branch_known_2 = {}
        branch_known_2['name'] = 'b-k-2'
        branch_known_2['commit_hash'] = '0000300003000030000300003000030000300003'
        branch_known_2['merge_target'] = {}
        branch_known_2['merge_target']['current_branch'] = {}
        branch_known_2['merge_target']['current_branch']['name'] = 'b-k-2'
        branch_known_2['merge_target']['current_branch']['commit_hash'] = '0000300003000030000300003000030000300003'
        branch_known_2['merge_target']['target_branch'] = {}
        branch_known_2['merge_target']['target_branch']['name'] = 'b-k-2-5'
        branch_known_2['merge_target']['target_branch']['commit_hash'] = '0000700007000070000700007000070000700007'


        branch_extracted_1 = {}
        branch_extracted_1['name'] = 'master'
        branch_extracted_1['commit_hash'] = '0000900009000090000900009000090000900009'

        branch_extracted_2 = {}
        branch_extracted_2['name'] = 'b-e-2'
        branch_extracted_2['commit_hash'] = '0000500005000050000500005000050000500005'

        known_branches = [branch_known_1, branch_known_2]
        extracted_branches = [branch_extracted_1, branch_extracted_2]

        res = self.fetcher.get_merge_target_from_branch_list(branch_merge_target, extracted_branches, known_branches)

        self.assertEqual('b-e-1', res['current_branch']['name'])
        self.assertEqual('0000400004000040000400004000040000400004', res['current_branch']['commit_hash'])
        self.assertEqual('master', res['target_branch']['name'])
        self.assertEqual('0000900009000090000900009000090000900009', res['target_branch']['commit_hash'])

    def test_get_merge_target_from_branch_list_found_in_itself(self):
        branch_merge_target = {}
        branch_merge_target['name'] = 'b-9'
        branch_merge_target['commit_hash'] = '0000900009000090000900009000090000900009'

        branch_known_1 = {}
        branch_known_1['name'] = 'b-k-1'
        branch_known_1['commit_hash'] = '0000200002000020000200002000020000200002'
        branch_known_1['merge_target'] = {}
        branch_known_1['merge_target']['current_branch'] = {}
        branch_known_1['merge_target']['current_branch']['name'] = 'b-k-1'
        branch_known_1['merge_target']['current_branch']['commit_hash'] = '0000200002000020000200002000020000200002'
        branch_known_1['merge_target']['target_branch'] = {}
        branch_known_1['merge_target']['target_branch']['name'] = 'b-k-1-5'
        branch_known_1['merge_target']['target_branch']['commit_hash'] = '0000800008000080000800008000080000800008'

        branch_known_2 = {}
        branch_known_2['name'] = 'b-k-2'
        branch_known_2['commit_hash'] = '0000300003000030000300003000030000300003'
        branch_known_2['merge_target'] = {}
        branch_known_2['merge_target']['current_branch'] = {}
        branch_known_2['merge_target']['current_branch']['name'] = 'b-k-2'
        branch_known_2['merge_target']['current_branch']['commit_hash'] = '0000300003000030000300003000030000300003'
        branch_known_2['merge_target']['target_branch'] = {}
        branch_known_2['merge_target']['target_branch']['name'] = 'b-k-2-5'
        branch_known_2['merge_target']['target_branch']['commit_hash'] = '0000700007000070000700007000070000700007'

        branch_extracted_1 = {}
        branch_extracted_1['name'] = 'b-e-1'
        branch_extracted_1['commit_hash'] = '0000400004000040000400004000040000400004'

        branch_extracted_2 = {}
        branch_extracted_2['name'] = 'b-e-2'
        branch_extracted_2['commit_hash'] = '0000500005000050000500005000050000500005'

        known_branches = [branch_known_1, branch_known_2]
        extracted_branches = [branch_extracted_1, branch_extracted_2]

        res = self.fetcher.get_merge_target_from_branch_list(branch_merge_target, extracted_branches, known_branches)

        self.assertEqual('b-9', res['current_branch']['name'])
        self.assertEqual('0000900009000090000900009000090000900009', res['current_branch']['commit_hash'])
        self.assertEqual('b-9', res['target_branch']['name'])
        self.assertEqual('0000900009000090000900009000090000900009', res['target_branch']['commit_hash'])

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

    @mock.patch('app.logic.bluesteelworker.download.CommandExecutioner.subprocess.call')
    def test_commands_get_diff_between_commits(self, mock_subprocess):
        commit_1 = '0000100001000010000100001000010000100001'
        commit_2 = '0000200002000020000200002000020000200002'

        mock_subprocess.return_value = 0
        self.create_paths(self.obj1)
        self.create_git_hidden_folder(settings.TMP_ROOT, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1')
        reports = self.fetcher.commands_get_diff_between_commits(self.obj1, commit_1, commit_2)

        name, args, side = mock_subprocess.mock_calls[0]
        self.assertEqual(['git', 'diff', commit_1, commit_2], args[0])

        self.assertEqual(1, mock_subprocess.call_count)

        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1', 'project')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1', 'log')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1', 'log', 'out.txt')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1', 'log', 'err.txt')))

        self.assertEqual(1, len(reports['commands']))

        self.assertEqual(0, reports['commands'][0]['result']['status'])
        self.assertEqual('git diff {0} {1}'.format(commit_1, commit_2), reports['commands'][0]['command'])
        self.assertEqual('', reports['commands'][0]['result']['error'])
        self.assertEqual('', reports['commands'][0]['result']['out'])

    def test_extract_diff_from_report(self):
        report1 = {}
        report1['command'] = 'git rev-parse master'
        report1['result'] = {}
        report1['result']['status'] = 0
        report1['result']['out'] = '0000100001000010000100001000010000100001'
        report1['result']['error'] = ''

        report2 = {}
        report2['command'] = 'git diff ...'
        report2['result'] = {}
        report2['result']['status'] = 0
        report2['result']['out'] = 'diff-long-long-text'
        report2['result']['error'] = ''

        obj = {}
        obj['status'] = True
        obj['commands'] = []
        obj['commands'].append(report1)
        obj['commands'].append(report2)

        diff = self.fetcher.extract_diff_from_report(obj)

        self.assertEqual('diff-long-long-text', diff)

    def test_extract_diff_from_report_without_non_utf_8_characters(self):
        report1 = {}
        report1['command'] = 'git rev-parse master'
        report1['result'] = {}
        report1['result']['status'] = 0
        report1['result']['out'] = '0000100001000010000100001000010000100001'
        report1['result']['error'] = ''

        report2 = {}
        report2['command'] = 'git diff ...'
        report2['result'] = {}
        report2['result']['status'] = 0
        report2['result']['out'] = 'this-is-a-text-that-\xa0-contains-non-utf-8-characters'
        report2['result']['error'] = ''

        obj = {}
        obj['status'] = True
        obj['commands'] = []
        obj['commands'].append(report1)
        obj['commands'].append(report2)

        diff = self.fetcher.extract_diff_from_report(obj)

        self.assertEqual('this-is-a-text-that--contains-non-utf-8-characters', diff)


    @mock.patch('app.logic.bluesteelworker.download.CommandExecutioner.subprocess.call')
    def test_step_get_diff_for_all_commits(self, mock_subprocess):
        mock_subprocess.return_value = 0
        self.create_paths(self.obj1)
        self.create_git_hidden_folder(settings.TMP_ROOT, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1')

        commit1 = {}
        commit1['hash'] = '0000100001000010000100001000010000100001'

        commit2 = {}
        commit2['hash'] = '0000200002000020000200002000020000200002'

        commit3 = {}
        commit3['hash'] = '0000300003000030000300003000030000300003'

        branch1 = {}
        branch1['name'] = 'name-1'
        branch1['commits'] = []
        branch1['commits'].append(commit1)
        branch1['commits'].append(commit2)
        branch1['commits'].append(commit3)

        branch2 = {}
        branch2['name'] = 'name-2'
        branch2['commits'] = []
        branch2['commits'].append(commit1)
        branch2['commits'].append(commit2)
        branch2['commits'].append(commit3)

        self.fetcher.branches_data = [branch1, branch2]

        res = self.fetcher.step_get_diff_for_all_commits(self.obj1)

        self.assertTrue(res)
        self.assertEqual(2, mock_subprocess.call_count)
        self.assertEqual(2, len(self.fetcher.diff_hash_dict))
        self.assertTrue('0000100001000010000100001000010000100001-0000200002000020000200002000020000200002' in self.fetcher.diff_hash_dict)
        self.assertTrue('0000200002000020000200002000020000200002-0000300003000030000300003000030000300003' in self.fetcher.diff_hash_dict)

        name1, args1, side1 = mock_subprocess.mock_calls[0]
        self.assertEqual(['git', 'diff', '0000100001000010000100001000010000100001', '0000200002000020000200002000020000200002'], args1[0])

        name2, args2, side2 = mock_subprocess.mock_calls[1]
        self.assertEqual(['git', 'diff', '0000200002000020000200002000020000200002', '0000300003000030000300003000030000300003'], args2[0])


    @mock.patch('app.logic.bluesteelworker.download.CommandExecutioner.subprocess.call')
    def test_step_local_branches(self, mock_subprocess):
        mock_subprocess.return_value = 0
        self.create_paths(self.obj1)
        self.create_git_hidden_folder(settings.TMP_ROOT, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1')

        self.fetcher.remote_branch_names = ['branch-1', 'branch-3', 'branch-5']
        self.fetcher.local_branch_names = ['branch-1', 'branch-2', 'branch-3', 'branch-4']

        res = self.fetcher.step_remove_local_branches(self.obj1)

        self.assertTrue(res)
        self.assertEqual(2, mock_subprocess.call_count)

        name1, args1, side1 = mock_subprocess.mock_calls[0]
        self.assertEqual(['git', 'branch', '-D', 'branch-2'], args1[0])

        name2, args2, side2 = mock_subprocess.mock_calls[1]
        self.assertEqual(['git', 'branch', '-D', 'branch-4'], args2[0])



