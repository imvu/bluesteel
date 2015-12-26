""" Feed model """

from django.db import models

class FeedEntry(models.Model):
    """ Feed """

    command_group = models.ForeignKey('commandrepo.CommandGroupEntry', related_name='feed_command_group')
    worker = models.ForeignKey('bluesteelworker.WorkerEntry', related_name='feed_worker', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'Feed: {0}'.format(self.id)

    def as_object(self):
        """ Returns feed as an object """
        obj = {}
        obj['id'] = self.id
        obj['command_group'] = self.command_group.as_object()
        obj['worker'] = self.worker.as_object()
        obj['date'] = str(self.created_at)
        return obj
