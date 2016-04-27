""" Bluesteel Project tests """

from django.test import TestCase
from django.utils import timezone
from app.logic.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.logic.gitrepo.models.GitProjectModel import GitProjectEntry
from app.logic.gitrepo.models.GitCommitModel import GitCommitEntry
from app.logic.gitrepo.models.GitUserModel import GitUserEntry
from app.logic.commandrepo.models.CommandGroupModel import CommandGroupEntry
from app.logic.commandrepo.models.CommandSetModel import CommandSetEntry
from app.logic.commandrepo.models.CommandModel import CommandEntry

class BluesteelProjectTestCase(TestCase):

    def setUp(self):
        self.git_project = GitProjectEntry.objects.create(
            url='http://www.test.com',
            name='git-project-28',
        )

        self.git_user1 = GitUserEntry.objects.create(
            project=self.git_project,
            name='user1',
            email='user1@test.com'
        )

        self.commit1 = GitCommitEntry.objects.create(project=self.git_project, commit_hash='0000100001000010000100001000010000100001', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())
        self.commit2 = GitCommitEntry.objects.create(project=self.git_project, commit_hash='0000200002000020000200002000020000200002', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())
        self.commit3 = GitCommitEntry.objects.create(project=self.git_project, commit_hash='0000300003000030000300003000030000300003', author=self.git_user1, author_date=timezone.now(), committer=self.git_user1, committer_date=timezone.now())

        self.command_group = CommandGroupEntry.objects.create()
        self.command_set = CommandSetEntry.objects.create(
            group=self.command_group
        )

        self.command = CommandEntry.objects.create(
            command_set=self.command_set,
            command='command-1 arg-2, arg-3',
            order=0
        )

        self.layout = BluesteelLayoutEntry.objects.create(
            name='layout-1',
        )

        self.project = BluesteelProjectEntry.objects.create(
            name='project-1',
            layout=self.layout,
            command_group=self.command_group,
            git_project=self.git_project,
        )


    def tearDown(self):
        pass

    def test_get_entry_as_object(self):
        obj = self.project.as_object()

        self.assertEqual('project-1', obj['name'])
        self.assertEqual('project-{0}'.format(self.project.id), self.project.get_uuid())
        self.assertEqual(1, len(obj['command_group']['command_sets']))

    def test_get_uuid(self):
        project_new = BluesteelProjectEntry.objects.create(
            name='project-28',
            layout=self.layout,
            command_group=self.command_group,
            git_project=self.git_project,
        )

        self.assertEqual('project-{0}'.format(project_new.id), project_new.get_uuid())

    def test_wipe_data(self):
        project_new = BluesteelProjectEntry.objects.create(
            name='project-28',
            layout=self.layout,
            command_group=self.command_group,
            git_project=self.git_project,
        )

        self.assertEqual(3, GitCommitEntry.objects.all().count())

        project_new.wipe_data()

        self.assertEqual(0, GitCommitEntry.objects.all().count())
