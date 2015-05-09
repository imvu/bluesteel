""" Command model """

from django.db import models
import json

# To allow 'OK' be a correct property name
#pylint: disable=C0103

class CommandEntry(models.Model):
    """ Command """

    OK = 0
    ERROR = 1
    STATUSES = (
        (OK, 'Ok'),
        (ERROR, 'Error'),
    )

    command_set = models.ForeignKey('commandrepo.CommandSetEntry', related_name='command_set')
    command = models.TextField(default='')
    out = models.TextField(default='')
    error = models.TextField(default='')
    exception = models.TextField(default='')
    status = models.IntegerField(choices=STATUSES, default=OK)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'Command:{0}, status:{1}'.format(self.command, self.status)

    def as_object(self):
        """ Returns a command entry as an object """
        status_values = ['OK', 'ERROR']

        obj = {}
        obj['command'] = json.loads(self.command)
        obj['out'] = self.out
        obj['error'] = self.error
        obj['exception'] = self.exception
        obj['status'] = status_values[self.status]
        obj['date_created_at'] = self.created_at
        return obj

    def set_status_from_str(self, status):
        """ Helps set the status from a string """
        if status == 'OK':
            self.status = CommandEntry.OK
        else:
            self.status = CommandEntry.ERROR
        self.save()

