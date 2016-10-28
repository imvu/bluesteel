""" BenchmarkDefinition model """

from django.db import models
from django.db.models import signals
from django.dispatch.dispatcher import receiver
from app.logic.commandrepo.models.CommandSetModel import CommandSetEntry

class BenchmarkDefinitionEntry(models.Model):
    """ Benchmark Definition """
    name = models.CharField(default='Default benchmark name', max_length=128)
    layout = models.ForeignKey('bluesteel.BluesteelLayoutEntry', related_name='benchmark_layout')
    project = models.ForeignKey('bluesteel.BluesteelProjectEntry', related_name='benchmark_project')
    command_set = models.ForeignKey('commandrepo.CommandSetEntry', related_name='benchmark_command_set')
    active = models.BooleanField(default=False)
    revision = models.IntegerField(default=0)
    max_fluctuation_percent = models.IntegerField(default=0)
    max_weeks_old_notify = models.IntegerField(default=1)
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
        obj['id'] = self.id
        obj['name'] = self.name
        obj['layout'] = {}
        obj['layout']['id'] = self.layout.id
        obj['layout']['name'] = self.layout.name
        obj['project'] = {}
        obj['project']['id'] = self.project.id
        obj['project']['name'] = self.project.name
        obj['command_set'] = self.command_set.as_object()
        obj['active'] = self.active
        obj['revision'] = self.revision
        obj['max_fluctuation_percent'] = self.max_fluctuation_percent
        obj['max_weeks_old_notify'] = {}
        obj['max_weeks_old_notify']['current_value'] = self.max_weeks_old_notify
        obj['max_weeks_old_notify']['current_name'] = ''
        obj['max_weeks_old_notify']['names'] = self.get_max_weeks_old_names_and_values()

        for val in obj['max_weeks_old_notify']['names']:
            if val['current']:
                obj['max_weeks_old_notify']['current_name'] = val['name']

        return obj

    def increment_revision(self):
        self.revision = self.revision + 1
        self.save()

    def get_max_weeks_old_names_and_values(self):
        """ Returns names, values, and current for all the possible weeks available """
        values = [
            {'name' : 'Allways', 'weeks' : -1},
            {'name' : 'Never', 'weeks' : 0},
            {'name' : '1 Week', 'weeks' : 1},
            {'name' : '2 Weeks', 'weeks' : 2},
            {'name' : '3 Weeks', 'weeks' : 3},
            {'name' : '1 Month', 'weeks' : 4},
            {'name' : '2 Months', 'weeks' : 8},
            {'name' : '3 Months', 'weeks' : 12},
            {'name' : '4 Months', 'weeks' : 16},
            {'name' : '5 Months', 'weeks' : 20},
            {'name' : '6 Months', 'weeks' : 24},
            {'name' : '1 Year', 'weeks' : 52},
            {'name' : '2 Years', 'weeks' : 104},
            {'name' : '3 Years', 'weeks' : 156},
            {'name' : '4 Years', 'weeks' : 208},
            {'name' : '5 Years', 'weeks' : 260},
            {'name' : '10 Years', 'weeks' : 520}
        ]

        for val in values:
            val['current'] = val['weeks'] == self.max_weeks_old_notify

        return values


@receiver(models.signals.post_delete)
def benchmark_def_entry_post_delete(sender, instance, **kwargs):
    """ This function will delete the command_set on any delete of this model """
    del kwargs
    if isinstance(instance, BenchmarkDefinitionEntry) and (sender == BenchmarkDefinitionEntry):
        signals.post_delete.disconnect(benchmark_def_entry_post_delete, sender=BenchmarkDefinitionEntry)
        try:
            if instance.command_set and instance.command_set.id != None:
                instance.command_set.delete()
        except CommandSetEntry.DoesNotExist:
            pass

        signals.post_delete.connect(benchmark_def_entry_post_delete, sender=BenchmarkDefinitionEntry)
