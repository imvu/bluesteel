""" Presenter Views tests """

from django.test import TestCase
from django.test import Client
from app.service.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.service.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.service.bluesteel.controllers.BluesteelProjectController import BluesteelProjectController
from app.service.bluesteel.controllers.BluesteelLayoutController import BluesteelLayoutController
from app.service.gitrepo.models.GitProjectModel import GitProjectEntry
from app.util.commandrepo.models.CommandModel import CommandEntry
from app.util.httpcommon import res
import json

class BluesteelViewLayoutTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.layout_1 = BluesteelLayoutEntry.objects.create(
            name='layout-1',
            archive='archive-28'
        )

    def tearDown(self):
        pass

    def test_save_bluesteel_layout(self):
        obj = {}
        obj['name'] = 'layout-2'
        obj['active'] = False
        obj['project_index_path'] = 0

        self.assertEqual(1, BluesteelLayoutEntry.objects.filter(name='layout-1').count())

        resp = self.client.post(
            '/main/layout/{0}/save/'.format(self.layout_1.id),
            data = json.dumps(obj),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual(1, BluesteelLayoutEntry.objects.filter(name='layout-2', active=False).count())

    def test_layout_become_inactive_because_project_index_not_correct(self):
        obj = {}
        obj['name'] = 'layout-1'
        obj['active'] = True
        obj['project_index_path'] = 0

        resp = self.client.post(
            '/main/layout/{0}/save/'.format(self.layout_1.id),
            data = json.dumps(obj),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual(False, BluesteelLayoutEntry.objects.all().first().active)
        self.assertEqual(0, BluesteelLayoutEntry.objects.all().first().project_index_path)

    def test_save_fails_because_name_not_correct(self):
        obj = {}
        obj['name'] = 'layout/1'
        obj['active'] = True
        obj['project_index_path'] = 0

        resp = self.client.post(
            '/main/layout/{0}/save/'.format(self.layout_1.id),
            data = json.dumps(obj),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(406, resp_obj['status'])
        self.assertEqual('layout-1', BluesteelLayoutEntry.objects.all().first().name)
        self.assertEqual(False, BluesteelLayoutEntry.objects.all().first().active)
        self.assertEqual(0, BluesteelLayoutEntry.objects.all().first().project_index_path)


    def test_layout_remains_active_because_project_index_is_correct(self):
        git_project_1 = GitProjectEntry.objects.create(
            url='http://www.test-1.com',
            name='git-project-1',
        )

        git_project_2 = GitProjectEntry.objects.create(
            url='http://www.test-2.com',
            name='git-project-2',
        )

        command_group_1 = BluesteelProjectController.create_default_command_group()
        command_group_2 = BluesteelProjectController.create_default_command_group()

        project_entry_1 = BluesteelProjectEntry.objects.create(
            layout=self.layout_1,
            name='project-1',
            command_group=command_group_1,
            git_project=git_project_1,
        )

        project_entry_2 = BluesteelProjectEntry.objects.create(
            layout=self.layout_1,
            name='project-2',
            command_group=command_group_2,
            git_project=git_project_2,
        )

        self.assertEqual(0, self.layout_1.project_index_path)

        obj = {}
        obj['name'] = 'layout-1'
        obj['active'] = True
        obj['project_index_path'] = 1

        resp = self.client.post(
            '/main/layout/{0}/save/'.format(self.layout_1.id),
            data = json.dumps(obj),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual(True, BluesteelLayoutEntry.objects.all().first().active)
        self.assertEqual(1, BluesteelLayoutEntry.objects.all().first().project_index_path)


    def test_save_bluesteel_layout_clamps_project_index_path_to_zero(self):
        obj = {}
        obj['name'] = 'layout-1'
        obj['active'] = False
        obj['project_index_path'] = 28

        resp = self.client.post(
            '/main/layout/{0}/save/'.format(self.layout_1.id),
            data = json.dumps(obj),
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual(0, BluesteelLayoutEntry.objects.all().first().project_index_path)


    def test_add_bluesteel_project_to_layout(self):
        self.assertEqual(1, BluesteelLayoutEntry.objects.all().count())
        self.assertEqual(0, BluesteelProjectEntry.objects.all().count())

        resp = self.client.post(
            '/main/layout/{0}/add/project/'.format(self.layout_1.id),
            data = '',
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual(1, BluesteelLayoutEntry.objects.all().count())
        self.assertEqual(1, BluesteelProjectEntry.objects.filter(order=0).count())

        resp = self.client.post(
            '/main/layout/{0}/add/project/'.format(self.layout_1.id),
            data = '',
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual(1, BluesteelLayoutEntry.objects.all().count())
        self.assertEqual(1, BluesteelProjectEntry.objects.filter(order=0).count())
        self.assertEqual(1, BluesteelProjectEntry.objects.filter(order=1).count())

    def test_add_bluesteel_project_to_layout(self):
        layout_entry = BluesteelLayoutController.create_new_default_layout()

        self.assertEqual(1, BluesteelLayoutEntry.objects.filter(id=layout_entry.id).count())
        self.assertEqual(1, BluesteelProjectEntry.objects.all().count())

        self.assertEqual(1, CommandEntry.objects.filter(order=0, command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=1, command='git reset --hard origin/master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=2, command='git clean -f -d -q').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=3, command='git fetch --all').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=4, command='git pull -r origin master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=5, command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=6, command='git submodule sync').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=7, command='git submodule update --init --recursive').count())

        resp = self.client.post(
            '/main/layout/{0}/delete/'.format(layout_entry.id),
            data = '',
            content_type='application/json')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual(0, BluesteelLayoutEntry.objects.filter(id=layout_entry.id).count())
        self.assertEqual(0, BluesteelProjectEntry.objects.all().count())
        self.assertEqual(0, CommandEntry.objects.all().count())

