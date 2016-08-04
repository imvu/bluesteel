""" Command Executioner tests """

from django.test import TestCase
from django.conf import settings
from app.logic.bluesteelworker.download.core.CommandExecutioner import CommandExecutioner
import os
import shutil
import mock

class CommandExecutionerTestCase(TestCase):

    def setUp(self):
        self.tmp_folder = os.path.join(settings.TMP_ROOT)

        if not os.path.exists(self.tmp_folder):
            os.makedirs(self.tmp_folder)

    def tearDown(self):
        if os.path.exists(self.tmp_folder):
            shutil.rmtree(self.tmp_folder)

    def test_clear_log_folder(self):
        project_path = os.path.join(self.tmp_folder, 'tmp-gitfetcher-folder', 'archive-28-0123ABC', 'test-repo-1', 'log')
        os.makedirs(project_path)
        file_log = open(os.path.join(project_path, 'log1.txt'), 'w')
        file_log.close()

        self.assertTrue(os.path.exists(os.path.join(project_path, 'log1.txt')))
        CommandExecutioner.clear_folder(project_path)
        self.assertTrue(os.path.exists(project_path))
        self.assertFalse(os.path.exists(os.path.join(project_path, 'log1.txt')))


    @mock.patch('app.logic.bluesteelworker.download.core.CommandExecutioner.subprocess.call')
    def test_fetch_project(self, mock_subprocess):
        mock_subprocess.return_value = 0
        commands = []
        commands.append(['ls'])
        commands.append(['cd', '..'])
        commands.append(['ls'])
        commands.append(['ps', 'aux'])

        CommandExecutioner.execute_command_list(
            commands,
            os.path.join(self.tmp_folder, 'log'),
            'project_cwd',
            True)

        name, args, side = mock_subprocess.mock_calls[0]
        self.assertEqual(['ls'], args[0])

        name, args, side = mock_subprocess.mock_calls[1]
        self.assertEqual(['cd', '..'], args[0])

        name, args, side = mock_subprocess.mock_calls[2]
        self.assertEqual(['ls'], args[0])

        name, args, side = mock_subprocess.mock_calls[3]
        self.assertEqual(['ps', 'aux'], args[0])

        self.assertEqual(4, mock_subprocess.call_count)

    def test_remove_non_ascii_characters(self):
        utf_str = u'Hi \xf3there!'

        ascii_str = CommandExecutioner.remove_non_ascii(utf_str)

        self.assertEqual(u'Hi  there!', ascii_str)
