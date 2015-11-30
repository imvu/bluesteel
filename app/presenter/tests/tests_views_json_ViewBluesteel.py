""" Bluesteel Views tests """

from django.test import TestCase
from django.test import Client
from app.service.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.service.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.service.gitrepo.models.GitProjectModel import GitProjectEntry
from app.util.commandrepo.models.CommandGroupModel import CommandGroupEntry
from app.util.commandrepo.models.CommandSetModel import CommandSetEntry
from app.util.commandrepo.models.CommandModel import CommandEntry
from app.util.httpcommon import res
import json

class BluesteelViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.layout_1 = BluesteelLayoutEntry.objects.create(
            name='layout-1',
        )

        self.layout_2 = BluesteelLayoutEntry.objects.create(
            name='layout-2',
        )

        self.layout_3 = BluesteelLayoutEntry.objects.create(
            name='layout-3',
        )


    def tearDown(self):
        pass

    def test_get_all_layouts_urls(self):
        resp = self.client.get('/main/layout/all/urls/')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(3, len(resp_obj['data']['layouts']))

        self.assertTrue('http://testserver/main/layout/1/' in resp_obj['data']['layouts'])
        self.assertTrue('http://testserver/main/layout/2/' in resp_obj['data']['layouts'])
        self.assertTrue('http://testserver/main/layout/3/' in resp_obj['data']['layouts'])

    def test_get_layout_1(self):
        git_project = GitProjectEntry.objects.create(
            url='http://www.test.com',
            name='git-project-28',
        )

        command_group = CommandGroupEntry.objects.create()
        command_set = CommandSetEntry.objects.create(
            group=command_group
        )

        command = CommandEntry.objects.create(
            command_set=command_set,
            command='command-1 arg-2, arg-3',
            order=0
        )

        project_1 = BluesteelProjectEntry.objects.create(
            name='project-1',
            layout=self.layout_1,
            command_group=command_group,
            git_project=git_project,
        )

        resp = self.client.get('/main/layout/1/')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(1, resp_obj['data']['id'])
        self.assertEqual('layout-1', resp_obj['data']['name'])
        self.assertEqual('archive-1', resp_obj['data']['uuid'])
        self.assertEqual('http://testserver/gitfeeder/feed/commit/project/1/', resp_obj['data']['projects'][0]['feed_url'])


    def test_get_layout_project_ids_and_names_and_selected(self):
        git_project = GitProjectEntry.objects.create(
            url='http://www.test.com',
            name='git-project-28',
        )

        command_group = CommandGroupEntry.objects.create()
        command_set = CommandSetEntry.objects.create(
            group=command_group
        )

        command = CommandEntry.objects.create(
            command_set=command_set,
            command='command-1 arg-2, arg-3',
            order=0
        )

        project_1 = BluesteelProjectEntry.objects.create(
            name='project-1',
            layout=self.layout_1,
            command_group=command_group,
            git_project=git_project,
        )

        project_2 = BluesteelProjectEntry.objects.create(
            name='project-2',
            layout=self.layout_1,
            command_group=command_group,
            git_project=git_project,
        )

        project_3 = BluesteelProjectEntry.objects.create(
            name='project-3',
            layout=self.layout_1,
            command_group=command_group,
            git_project=git_project,
        )

        self.layout_1.project_index_path = 2
        self.layout_1.save()

        resp = self.client.get('/main/layout/1/projects/info/')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(3, len(resp_obj['data']['projects']))

        self.assertEqual('project-1', resp_obj['data']['projects'][0]['name'])
        self.assertEqual(project_1.id, resp_obj['data']['projects'][0]['id'])
        self.assertEqual(False, resp_obj['data']['projects'][0]['selected'])

        self.assertEqual('project-2', resp_obj['data']['projects'][1]['name'])
        self.assertEqual(project_2.id, resp_obj['data']['projects'][1]['id'])
        self.assertEqual(False, resp_obj['data']['projects'][1]['selected'])

        self.assertEqual('project-3', resp_obj['data']['projects'][2]['name'])
        self.assertEqual(project_3.id, resp_obj['data']['projects'][2]['id'])
        self.assertEqual(True, resp_obj['data']['projects'][2]['selected'])
