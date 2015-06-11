""" Command model """

from django.db import models
from app.util.commandrepo.models.CommandResultModel import CommandResultEntry

class CommandEntry(models.Model):
    """ Command """

    command_set = models.ForeignKey('commandrepo.CommandSetEntry', related_name='command_set')
    command = models.TextField(default='')
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'Command:{0}, status:{1}'.format(self.command, self.status)

    def as_object(self):
        """ Returns a command entry as an object """

        obj = {}
        obj['command'] = self.command
        obj['date_created_at'] = self.created_at
        obj['result'] = {}

        entry = CommandResultEntry.objects.all().filter(command_id=self.id).first()
        if entry:
            obj['result'] = entry.as_object()

        return obj
