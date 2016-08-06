""" Command to write update hash of worker files """

from django.core.management.base import BaseCommand
from app.logic.bluesteelworker.models.WorkerFilesHashModel import WorkerFilesHashEntry

class Command(BaseCommand):
    args = ''
    help = 'Update the hash for all the worker files'

    def handle(self, *args, **options):
        """ Sends out all the stacked emails ready to send """
        WorkerFilesHashEntry.objects.all().delete()

        WorkerFilesHashEntry.objects.create(
            files_hash='0000100001000010000100001000010000100001')
