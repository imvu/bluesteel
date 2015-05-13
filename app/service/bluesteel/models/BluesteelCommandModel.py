""" BlueSteelCommand model """

from django.db import models

class BluesteelCommandEntry(models.Model):
    """ BlueSteel Command """

    order = models.IntegerField(default=0)
    command = models.CharField(default='', max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'BlueSteelCommand command:{0}, order:{1}'.format(self.command, self.order)

