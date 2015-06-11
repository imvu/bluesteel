""" Command Result model """

from django.db import models

class CommandResultEntry(models.Model):
    """ Command Result """

    command = models.OneToOneField('commandrepo.CommandEntry')
    out = models.TextField(default='')
    error = models.TextField(default='')
    status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'Command Result - Command:{0}, status:{1}'.format(self.command.id, self.status)

    def as_object(self):
        """ Returns a command result as an object """
        obj = {}
        obj['out'] = self.out
        obj['error'] = self.error
        obj['status'] = self.status
        return obj

