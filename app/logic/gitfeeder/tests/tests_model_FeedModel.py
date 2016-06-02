""" GitFeederController tests """

from django.test import TestCase
from django.contrib.auth.models import User
from app.logic.gitfeeder.models.FeedModel import FeedEntry
from app.logic.gitrepo.models.GitProjectModel import GitProjectEntry
from app.logic.gitrepo.models.GitUserModel import GitUserEntry
from app.logic.bluesteelworker.models.WorkerModel import WorkerEntry
from app.logic.commandrepo.models.CommandGroupModel import CommandGroupEntry

class FeedModelTestCase(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user('user1@test.com', 'user1@test.com', 'pass1')

        self.worker1 = WorkerEntry.objects.create(
            name='worker-name-1',
            uuid='uuid-worker-1',
            operative_system='osx',
            description='long-description-1',
            user=self.user1,
            git_feeder=False
        )

        self.git_project1 = GitProjectEntry.objects.create(url='http://test/')
        self.git_user1 = GitUserEntry.objects.create(
            project=self.git_project1,
            name='user1',
            email='user1@test.com'
        )

    def tearDown(self):
        pass

    def test_feed_is_removed_if_git_project_is_deleted(self):
        command_group = CommandGroupEntry.objects.create(user=self.user1)

        FeedEntry.objects.create(command_group=command_group, worker=self.worker1, git_project=self.git_project1)

        self.assertEqual(1, FeedEntry.objects.all().count())

        self.git_project1.delete()

        self.assertEqual(0, FeedEntry.objects.all().count())

    def test_feed_deletion_also_deletes_command_group(self):
        command_group = CommandGroupEntry.objects.create(user=self.user1)
        feed_entry = FeedEntry.objects.create(command_group=command_group, worker=self.worker1, git_project=self.git_project1)

        self.assertEqual(1, FeedEntry.objects.all().count())
        self.assertEqual(1, CommandGroupEntry.objects.all().count())

        feed_entry.delete()

        self.assertEqual(0, FeedEntry.objects.all().count())
        self.assertEqual(0, CommandGroupEntry.objects.all().count())
