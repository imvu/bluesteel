""" CommandReport model """

from django.db import models

class CommandReportEntry(models.Model):
    """ CommandReport """

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'CommandReport:{0}'.format(self.id)

