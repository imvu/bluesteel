""" Hash Worker Files tests """

from django.test import TestCase
from django.conf import settings
from django.core.management import call_command
from django.utils.six import StringIO
from app.logic.bluesteelworker.models.WorkerFilesHashModel import WorkerFilesHashEntry
from app.logic.bluesteelworker.download.core.FileHasher import FileHasher
import os
import shutil

class ManagementHashWorkerFilesTestCase(TestCase):

    def setUp(self):
        self.tmp_folder = os.path.join(settings.TMP_ROOT)
        self.folder_to_hash = os.path.join(self.tmp_folder, 'folder_to_hash')


        if not os.path.exists(self.tmp_folder):
            os.makedirs(self.tmp_folder)

        if not os.path.exists(self.folder_to_hash):
            os.makedirs(self.folder_to_hash)

    def tearDown(self):
        if os.path.exists(self.tmp_folder):
            shutil.rmtree(self.tmp_folder)

    def create_files_to_hash(self):
        file_1 = open(os.path.join(self.folder_to_hash, 'file1.txt'), 'w')
        file_2 = open(os.path.join(self.folder_to_hash, 'file2.txt'), 'w')
        file_3 = open(os.path.join(self.folder_to_hash, 'file3.txt'), 'w')
        file_4 = open(os.path.join(self.folder_to_hash, 'file4.io'), 'w')

        file_1.write('1111')
        file_2.write('2222')
        file_3.write('3333')
        file_4.write('4444')

        file_1.close()
        file_2.close()
        file_3.close()
        file_4.close()

    def test_call_command(self):
        out = StringIO()
        call_command('hash_worker_files', stdout=out)
        self.assertIn('', out.getvalue())

        # Not sure if allow that this test keeps track of the real hash of the download/core folder
        self.assertEqual(1, WorkerFilesHashEntry.objects.all().count())
        self.assertEqual(40, len(WorkerFilesHashEntry.objects.all().first().files_hash))


    def test_hash_files_inside_folder(self):
        self.create_files_to_hash()

        sha_hash = FileHasher.get_hash_from_files_in_a_folder(self.folder_to_hash, ['.txt'])

        self.assertEqual('d1fa7a05f436d17c73b3d9f79da32e44b588368f', sha_hash)

