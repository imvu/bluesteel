""" BlueSteelCommand Set model """

from django.db import models

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

