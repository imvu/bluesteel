""" BlueSteelCommand Set model """

from django.db import models
from app.service.bluesteel.models.BluesteelCommandModel import BluesteelCommandEntry

class BluesteelCommandSetEntry(models.Model):
    """ BlueSteel Command Set """

    CLONE = 0
    FETCH = 1
    PROJECT_COMMAND_SET_TYPE = (
        (CLONE, 'CLONE'),
        (FETCH, 'FETCH'),
    )

    bluesteel_project = models.ForeignKey('bluesteel.BluesteelProjectEntry', related_name='bluesteel_project')
    command_set_type = models.IntegerField(choices=PROJECT_COMMAND_SET_TYPE, default=CLONE)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'Bluesteel Command set ID:{0}'.format(self.id)

    def as_object(self):
        """ Return the command set as an object """
        obj = {}
        obj['type'] = self.PROJECT_COMMAND_SET_TYPE[int(self.command_set_type)][1]

        comm_entries = BluesteelCommandEntry.objects.all().filter(bluesteel_command_set=self.id).order_by('order')

        comms = []
        for comm in comm_entries:
            comms.append(comm.as_object())
        obj['commands'] = comms
        return obj

