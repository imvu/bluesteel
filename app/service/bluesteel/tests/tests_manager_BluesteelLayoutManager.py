""" Bluesteel Layout Manager tests """

from django.test import TestCase
from app.service.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.service.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.service.bluesteel.managers.BluesteelLayoutManager import BluesteelLayoutManager
from app.service.gitrepo.models.GitProjectModel import GitProjectEntry
from app.util.httpcommon import res
import json

class BluesteelLayoutManagerTestCase(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_default_layout_entry(self):
        self.assertEqual(0, BluesteelLayoutEntry.objects.all().count())
        self.assertEqual(0, BluesteelProjectEntry.objects.all().count())

        new_entry = BluesteelLayoutEntry.objects.create_new_default_layout()

        self.assertEqual(1, BluesteelLayoutEntry.objects.all().count())
        self.assertEqual(1, BluesteelProjectEntry.objects.all().count())
