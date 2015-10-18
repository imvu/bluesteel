""" Bluesteel Layout Controller tests """

from django.test import TestCase
from app.service.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.service.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.service.bluesteel.controllers.BluesteelLayoutController import BluesteelLayoutController
from app.service.gitrepo.models.GitProjectModel import GitProjectEntry
from app.util.commandrepo.models.CommandModel import CommandEntry
from app.util.httpcommon import res
import json

class BluesteelLayoutControllerTestCase(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_default_layout_entry(self):
        self.assertEqual(0, BluesteelLayoutEntry.objects.all().count())
        self.assertEqual(0, BluesteelProjectEntry.objects.all().count())

        new_entry = BluesteelLayoutController.create_new_default_layout()

        self.assertEqual(1, BluesteelLayoutEntry.objects.all().count())
        self.assertEqual(1, BluesteelProjectEntry.objects.all().count())

        self.assertEqual(1, CommandEntry.objects.filter(order=0, command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=1, command='git reset --hard origin/master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=2, command='git clean -f -d -q').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=3, command='git fetch --all').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=4, command='git pull -r origin master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=5, command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=6, command='git submodule sync').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=7, command='git submodule update --init --recursive').count())

    def test_delete_layout_entry(self):
        self.assertEqual(0, BluesteelLayoutEntry.objects.all().count())
        self.assertEqual(0, BluesteelProjectEntry.objects.all().count())

        new_entry = BluesteelLayoutController.create_new_default_layout()

        self.assertEqual(1, BluesteelLayoutEntry.objects.all().count())
        self.assertEqual(1, BluesteelProjectEntry.objects.all().count())

        self.assertEqual(1, CommandEntry.objects.filter(order=0, command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=1, command='git reset --hard origin/master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=2, command='git clean -f -d -q').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=3, command='git fetch --all').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=4, command='git pull -r origin master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=5, command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=6, command='git submodule sync').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=7, command='git submodule update --init --recursive').count())

        BluesteelLayoutController.delete_layout(new_entry)

        self.assertEqual(0, BluesteelLayoutEntry.objects.all().count())
        self.assertEqual(0, BluesteelProjectEntry.objects.all().count())
        self.assertEqual(0, CommandEntry.objects.all().count())
