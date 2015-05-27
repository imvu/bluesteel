""" BlueSteelCommand model """

from django.db import models

class BluesteelCommandEntry(models.Model):
    """ BlueSteel Command """

    bluesteel_command_set = models.ForeignKey(
        'bluesteel.BluesteelCommandSetEntry',
        related_name='bluesteel_command_set',
        null=True
    )
    order = models.IntegerField(default=0)
    command = models.CharField(default='', max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'BlueSteelCommand command:{0}, order:{1}'.format(self.command, self.order)

    def as_object(self):
        obj = {}
        obj['command'] = self.command
        obj['order'] = self.order
        return obj
