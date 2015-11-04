""" CommandSet model """

from django.db import models
from app.util.commandrepo.models.CommandModel import CommandEntry

class CommandSetEntry(models.Model):
    """ CommandSet """

    group = models.ForeignKey('commandrepo.CommandGroupEntry', related_name='command_group', null=True)
    name = models.TextField(default='')
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'CommandSet:{0}'.format(self.id)

    def as_object(self):
        """ Returns the command set as an object """
        obj = {}
        obj['name'] = self.name
        obj['order'] = self.order
        obj['commands'] = []

        command_list = CommandEntry.objects.all().filter(command_set__id=self.id).order_by('order')
        for command in command_list:
            obj['commands'].append(command.as_object())

        return obj
