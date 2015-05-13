""" BlueSteelCommand Set model """

from django.db import models

class BluesteelCommandSetEntry(models.Model):
    """ BlueSteel Command Set """

    bluesteel_project = models.ForeignKey('bluesteel.BluesteelProjectEntry', related_name='bluesteel_project')
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'Bluesteel Command set ID:{0}'.format(self.id)

