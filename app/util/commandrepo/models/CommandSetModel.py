""" CommandSet model """

from django.db import models

class CommandSetEntry(models.Model):
    """ CommandSet """

    report = models.ForeignKey('commandrepo.CommandReportEntry', related_name='command_repo')
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'CommandSet:{0}'.format(self.id)

