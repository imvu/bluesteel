""" BlueSteelLayout model """

from django.db import models

class BluesteelLayoutEntry(models.Model):
    """ BlueSteel Layout """
    name = models.CharField(default='', max_length=50)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'Bluesteel Layout name:{0}'.format(
            self.name
        )

