""" Command to write update hash of worker files """

import os
from django.core.management.base import BaseCommand
from app.logic.bluesteelworker.models.WorkerFilesHashModel import WorkerFilesHashEntry
from app.logic.bluesteelworker.download.core.FileHasher import FileHasher

class Command(BaseCommand):
    args = ''
    help = 'Update the hash for all the worker files'

    def handle(self, *args, **options):
        """ Update Worker Files hash """
        WorkerFilesHashEntry.objects.all().delete()

        this_folder_path = os.path.dirname(os.path.dirname(__file__))
        core_folder_path = os.path.join(this_folder_path, '..', 'download', 'core')

        sha_hash = FileHasher.get_hash_from_files_in_a_folder(core_folder_path, ['.py', '.json'])

        WorkerFilesHashEntry.objects.create(
            files_hash=sha_hash)
