""" Bluesteel Project Manager tests """

from django.test import TestCase
from app.service.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.service.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.service.bluesteel.controllers.BluesteelProjectController import BluesteelProjectController
from app.service.gitrepo.models.GitProjectModel import GitProjectEntry
from app.util.commandrepo.models.CommandModel import CommandEntry
from app.util.httpcommon import res
import json

class BluesteelProjectControllerTestCase(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_default_project_entry(self):
        self.assertEqual(0, BluesteelProjectEntry.objects.all().count())

        layout_entry = BluesteelLayoutEntry.objects.create(
            name='name',
        )

        new_entry = BluesteelProjectController.create_default_project(
            layout=layout_entry,
            name='project-name',
            order=28
        )

        self.assertEqual(1, BluesteelProjectEntry.objects.all().count())
        self.assertEqual(layout_entry, BluesteelProjectEntry.objects.all().first().layout)
        self.assertEqual('project-name', BluesteelProjectEntry.objects.all().first().name)
        self.assertEqual(28, BluesteelProjectEntry.objects.all().first().order)

        self.assertEqual(1, CommandEntry.objects.filter(order=0, command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=1, command='git reset --hard origin/master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=2, command='git clean -f -d -q').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=3, command='git fetch --all').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=4, command='git pull -r origin master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=5, command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=6, command='git submodule sync').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=7, command='git submodule update --init --recursive').count())

