""" Feed model """

from django.db import models
from django.db.models import signals
from django.dispatch.dispatcher import receiver
from app.logic.commandrepo.models.CommandGroupModel import CommandGroupEntry

class FeedEntry(models.Model):
    """ Feed """

    command_group = models.ForeignKey('commandrepo.CommandGroupEntry', related_name='feed_command_group')
    worker = models.ForeignKey('bluesteelworker.WorkerEntry', related_name='feed_worker', blank=True, null=True)
    git_project = models.ForeignKey('gitrepo.GitProjectEntry', related_name='feed_git_project', blank=True, null=True)
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
        obj['git_project'] = {}

        if self.git_project:
            obj['git_project']['id'] = self.git_project.id
            obj['git_project']['url'] = self.git_project.url
            obj['git_project']['name'] = self.git_project.name
        else:
            obj['git_project']['id'] = -1
            obj['git_project']['url'] = ''
            obj['git_project']['name'] = ''

        obj['date'] = str(self.created_at)
        return obj


@receiver(models.signals.post_delete)
def feed_entry_post_delete(sender, instance, **kwargs):
    """ This function will delete the command_group on any delete of this model """
    del kwargs
    if isinstance(instance, FeedEntry) and (sender == FeedEntry):
        signals.post_delete.disconnect(feed_entry_post_delete, sender=FeedEntry)
        try:
            if instance.command_group and instance.command_group.id is not None:
                instance.command_group.delete()
        except CommandGroupEntry.DoesNotExist:
            pass

        signals.post_delete.connect(feed_entry_post_delete, sender=FeedEntry)
