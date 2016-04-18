""" Bluesteel Layout Controller tests """

from django.test import TestCase
from app.logic.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.logic.bluesteel.controllers.BluesteelLayoutController import BluesteelLayoutController
from app.logic.gitrepo.models.GitProjectModel import GitProjectEntry
from app.logic.commandrepo.models.CommandModel import CommandEntry
from app.logic.httpcommon import res
from app.logic.httpcommon.Page import Page
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

        self.assertEqual(1, CommandEntry.objects.filter(order=0, command='git reset HEAD').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=1, command='git checkout -- .').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=2, command='git clean -d -f -q').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=3, command='git submodule sync --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=4, command='git submodule update --init --recursive --force').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=5, command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=6, command='git reset --hard origin/master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=7, command='git clean -d -f -q').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=8, command='git fetch --all').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=9, command='git pull -r origin master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=10, command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=11, command='git submodule sync --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=12, command='git submodule update --init --recursive --force').count())

    def test_delete_layout_entry(self):
        self.assertEqual(0, BluesteelLayoutEntry.objects.all().count())
        self.assertEqual(0, BluesteelProjectEntry.objects.all().count())

        new_entry = BluesteelLayoutController.create_new_default_layout()

        self.assertEqual(1, BluesteelLayoutEntry.objects.all().count())
        self.assertEqual(1, BluesteelProjectEntry.objects.all().count())

        self.assertEqual(1, CommandEntry.objects.filter(order=0, command='git reset HEAD').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=1, command='git checkout -- .').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=2, command='git clean -d -f -q').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=3, command='git submodule sync --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=4, command='git submodule update --init --recursive --force').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=5, command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=6, command='git reset --hard origin/master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=7, command='git clean -d -f -q').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=8, command='git fetch --all').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=9, command='git pull -r origin master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=10, command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=11, command='git submodule sync --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=12, command='git submodule update --init --recursive --force').count())

        BluesteelLayoutController.delete_layout(new_entry)

        self.assertEqual(0, BluesteelLayoutEntry.objects.all().count())
        self.assertEqual(0, BluesteelProjectEntry.objects.all().count())
        self.assertEqual(0, CommandEntry.objects.all().count())


    def test_get_paginated_layouts(self):
        layout_1 = BluesteelLayoutController.create_new_default_layout()
        layout_2 = BluesteelLayoutController.create_new_default_layout()
        layout_3 = BluesteelLayoutController.create_new_default_layout()
        layout_4 = BluesteelLayoutController.create_new_default_layout()
        layout_5 = BluesteelLayoutController.create_new_default_layout()
        layout_6 = BluesteelLayoutController.create_new_default_layout()
        layout_7 = BluesteelLayoutController.create_new_default_layout()

        layouts_1, page_indices1 = BluesteelLayoutController.get_paginated_layouts_as_objects(Page(3, 1))
        layouts_2, page_indices2 = BluesteelLayoutController.get_paginated_layouts_as_objects(Page(3, 2))
        layouts_3, page_indices3 = BluesteelLayoutController.get_paginated_layouts_as_objects(Page(3, 3))


        self.assertEqual(3, len(layouts_1))
        self.assertEqual(layout_7.id, layouts_1[0]['id'])
        self.assertEqual(layout_6.id, layouts_1[1]['id'])
        self.assertEqual(layout_5.id, layouts_1[2]['id'])
        self.assertEqual(1, page_indices1['prev'])
        self.assertEqual(1, page_indices1['current'])
        self.assertEqual(2, page_indices1['next'])
        self.assertEqual([1, 2, 3], page_indices1['page_indices'])

        self.assertEqual(3, len(layouts_2))
        self.assertEqual(layout_4.id, layouts_2[0]['id'])
        self.assertEqual(layout_3.id, layouts_2[1]['id'])
        self.assertEqual(layout_2.id, layouts_2[2]['id'])
        self.assertEqual(1, page_indices2['prev'])
        self.assertEqual(2, page_indices2['current'])
        self.assertEqual(3, page_indices2['next'])
        self.assertEqual([1, 2, 3], page_indices2['page_indices'])

        self.assertEqual(1, len(layouts_3))
        self.assertEqual(layout_1.id, layouts_3[0]['id'])
        self.assertEqual(2, page_indices3['prev'])
        self.assertEqual(3, page_indices3['current'])
        self.assertEqual(3, page_indices3['next'])
        self.assertEqual([1, 2, 3], page_indices3['page_indices'])
