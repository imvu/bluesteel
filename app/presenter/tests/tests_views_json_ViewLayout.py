""" Presenter Views tests """

from django.test import TestCase
from django.test import Client
from app.logic.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.logic.bluesteel.controllers.BluesteelProjectController import BluesteelProjectController
from app.logic.bluesteel.controllers.BluesteelLayoutController import BluesteelLayoutController
from app.logic.gitrepo.models.GitProjectModel import GitProjectEntry
from app.logic.commandrepo.models.CommandModel import CommandEntry
from app.logic.httpcommon import res
import json

class BluesteelViewLayoutTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.layout_1 = BluesteelLayoutEntry.objects.create(
            name='layout-1',
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


    def test_get_layout_list(self):
        layout_2 = BluesteelLayoutEntry.objects.create(name='layout-2')
        layout_3 = BluesteelLayoutEntry.objects.create(name='layout-3')

        resp = self.client.get('/main/layout/list/')

        res.check_cross_origin_headers(self, resp)
        resp_obj = json.loads(resp.content)

        self.assertEqual(200, resp_obj['status'])
        self.assertEqual(3, len(resp_obj['data']['layouts']))
        self.assertEqual('/main/layout/1/project/list/', resp_obj['data']['layouts'][0]['url']['project_list'])
        self.assertEqual('/main/layout/2/project/list/', resp_obj['data']['layouts'][1]['url']['project_list'])
        self.assertEqual('/main/layout/3/project/list/', resp_obj['data']['layouts'][2]['url']['project_list'])

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

        self.assertEqual(1, CommandEntry.objects.filter(order=0, command='git reset HEAD').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=1, command='git checkout -- .').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=2, command='git clean -d -f -q').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=3, command='git submodule sync --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=4, command='git submodule update --init --recursive --force').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=5, command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=6, command='git reset --hard origin/master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=7, command='git clean -d -f -q').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=8, command='git fetch --all -p').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=9, command='git pull -r origin master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=10, command='git checkout master').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=11, command='git submodule sync --recursive').count())
        self.assertEqual(1, CommandEntry.objects.filter(order=12, command='git submodule update --init --recursive --force').count())

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

