""" Git Feed Views reports tests """

from django.test import TestCase
from django.test import Client
from django.conf import settings
from django.contrib.auth.models import User
from app.logic.commandrepo.models.CommandGroupModel import CommandGroupEntry
from app.logic.commandrepo.models.CommandSetModel import CommandSetEntry
from app.logic.commandrepo.models.CommandModel import CommandEntry
from app.logic.commandrepo.models.CommandResultModel import CommandResultEntry
from app.logic.httpcommon import res
import json

class ViewJsonCommandTestCase(TestCase):

    def setUp(self):
        self.client = Client()

        self.user1 = User.objects.create_user('user1@test.com', 'user1@test.com', 'pass')
        self.user1.save()

    def tearDown(self):
        pass

    def test_command_can_be_downloaded(self):
        com_group = CommandGroupEntry.objects.create(user=self.user1)
        com_set = CommandSetEntry.objects.create(group=com_group, name='name', order=0)
        com = CommandEntry.objects.create(command_set=com_set, command='command-1', order=0)
        com_res = CommandResultEntry.objects.create(
            command=com,
            out='out-command-1',
            error='error-1',
            status=28
        )

        json_obj = com.as_object()

        resp = self.client.get('/main/command/{0}/download/json/'.format(com.id))

        self.assertEquals('attachment; filename=Command-{0}.json'.format(com.id), resp.get('Content-Disposition'))
        self.assertEquals(json_obj, json.loads(resp.content))

    def test_command_can_not_be_downloaded_because_doesnt_exist(self):
        json_obj = {}
        json_obj['msg'] = 'Command with id 28 not found'

        resp = self.client.get('/main/command/28/download/json/')

        self.assertEquals('attachment; filename=Command-28.json', resp.get('Content-Disposition'))
        self.assertEquals(json_obj, json.loads(resp.content))
