""" BenchmarkDefinition model """

from django.db import models
from django.db.models import signals
from django.dispatch.dispatcher import receiver

class BenchmarkDefinitionEntry(models.Model):
    """ Benchmark Definition """
    name = models.CharField(default='Default benchmark name', max_length=128)
    layout = models.ForeignKey('bluesteel.BluesteelLayoutEntry', related_name='benchmark_layout')
    project = models.ForeignKey('bluesteel.BluesteelProjectEntry', related_name='benchmark_project')
    command_set = models.ForeignKey('commandrepo.CommandSetEntry', related_name='benchmark_command_set')
    revision = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'Benchmark Definition id:{0} name:{1}'.format(
            self.id,
            self.name,
        )

    def as_object(self):
        """ Returns Benchmark Definition as an object"""
        obj = {}
        obj['name'] = self.name
        obj['layout'] = self.layout.as_object()
        obj['project'] = self.project.as_object()
        obj['command_set'] = self.command_set.as_object()
        obj['revision'] = self.revision
        return obj

    def increment_revision(self):
        self.revision = self.revision + 1
        self.save()


@receiver(models.signals.post_delete)
def benchmark_def_entry_post_delete(sender, instance, **kwargs):
    """ This function will delete the command_set on any delete of this model """
    del kwargs
    if isinstance(instance, BenchmarkDefinitionEntry) and (sender == BenchmarkDefinitionEntry):
        signals.post_delete.disconnect(benchmark_def_entry_post_delete, sender=BenchmarkDefinitionEntry)
        from app.logic.commandrepo.models.CommandSetModel import CommandSetEntry
        try:
            if instance.command_set and instance.command_set.id != None:
                instance.command_set.delete()
        except CommandSetEntry.DoesNotExist:
            pass

        signals.post_delete.connect(benchmark_def_entry_post_delete, sender=BenchmarkDefinitionEntry)
