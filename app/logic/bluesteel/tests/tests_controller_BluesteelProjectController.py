""" Bluesteel Project Manager tests """

from django.test import TestCase
from app.logic.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.logic.bluesteel.controllers.BluesteelProjectController import BluesteelProjectController
from app.logic.gitrepo.models.GitProjectModel import GitProjectEntry
from app.logic.commandrepo.models.CommandModel import CommandEntry
from app.logic.commandrepo.models.CommandGroupModel import CommandGroupEntry
from app.logic.commandrepo.models.CommandSetModel import CommandSetEntry
from app.logic.httpcommon import res
from app.logic.httpcommon.Page import Page
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

        self.assertEqual(1, CommandGroupEntry.objects.all().count())
        self.assertEqual(2, CommandSetEntry.objects.all().count())
        self.assertEqual('CLONE', CommandSetEntry.objects.filter(order=0).first().name)
        self.assertEqual('FETCH', CommandSetEntry.objects.filter(order=1).first().name)

        self.assertEqual(1, CommandEntry.objects.filter(order=0, command='git reset HEAD').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=1, command='git checkout -- .').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=2, command='git clean -d -f -q').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=3, command='git submodule sync --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=4, command='git submodule update --init --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=5, command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=6, command='git reset --hard origin/master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=7, command='git clean -d -f -q').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=8, command='git fetch --all').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=9, command='git pull -r origin master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=10, command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=11, command='git submodule sync --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=12, command='git submodule update --init --recursive').count())


    def test_get_paginated_projects(self):
        layout_entry = BluesteelLayoutEntry.objects.create(name='name')

        project_1 = BluesteelProjectController.create_default_project(layout=layout_entry, name='project-name-1', order=28)
        project_2 = BluesteelProjectController.create_default_project(layout=layout_entry, name='project-name-2', order=27)
        project_3 = BluesteelProjectController.create_default_project(layout=layout_entry, name='project-name-3', order=26)
        project_4 = BluesteelProjectController.create_default_project(layout=layout_entry, name='project-name-4', order=25)
        project_5 = BluesteelProjectController.create_default_project(layout=layout_entry, name='project-name-5', order=24)
        project_6 = BluesteelProjectController.create_default_project(layout=layout_entry, name='project-name-6', order=23)
        project_7 = BluesteelProjectController.create_default_project(layout=layout_entry, name='project-name-7', order=22)

        projects_1, page_indices_1 = BluesteelProjectController.get_paginated_projects_as_objects(Page(3, 1))
        projects_2, page_indices_2 = BluesteelProjectController.get_paginated_projects_as_objects(Page(3, 2))
        projects_3, page_indices_3 = BluesteelProjectController.get_paginated_projects_as_objects(Page(3, 3))

        self.assertEqual(3, len(projects_1))
        self.assertEqual(project_7.id, projects_1[0]['id'])
        self.assertEqual(project_6.id, projects_1[1]['id'])
        self.assertEqual(project_5.id, projects_1[2]['id'])
        self.assertEqual(1, page_indices_1['prev'])
        self.assertEqual(1, page_indices_1['current'])
        self.assertEqual(2, page_indices_1['next'])
        self.assertEqual([1, 2, 3], page_indices_1['page_indices'])

        self.assertEqual(3, len(projects_2))
        self.assertEqual(project_4.id, projects_2[0]['id'])
        self.assertEqual(project_3.id, projects_2[1]['id'])
        self.assertEqual(project_2.id, projects_2[2]['id'])
        self.assertEqual(1, page_indices_2['prev'])
        self.assertEqual(2, page_indices_2['current'])
        self.assertEqual(3, page_indices_2['next'])
        self.assertEqual([1, 2, 3], page_indices_2['page_indices'])

        self.assertEqual(1, len(projects_3))
        self.assertEqual(project_1.id, projects_3[0]['id'])
        self.assertEqual(2, page_indices_3['prev'])
        self.assertEqual(3, page_indices_3['current'])
        self.assertEqual(3, page_indices_3['next'])
        self.assertEqual([1, 2, 3], page_indices_3['page_indices'])
