""" CommandGroup model """

from django.db import models
from app.util.commandrepo.models.CommandSetModel import CommandSetEntry
from app.util.commandrepo.managers.CommandGroupManager import CommandGroupManager

class CommandGroupEntry(models.Model):
    """ CommandGroup """

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    objects = CommandGroupManager()

    def __unicode__(self):
        return u'CommandGroup:{0}'.format(self.id)

    def as_object(self):
        """ Returns a Command Group Entry as an object """
        obj = {}
        obj['command_sets'] = []

        sets_list = CommandSetEntry.objects.all().filter(group_id=self.id).order_by('order')

        for entry in sets_list:
            obj['command_sets'].append(entry.as_object())
        return obj

