""" BenchmarkDefinitionWorkerPass model """

from django.db import models

class BenchmarkDefinitionWorkerPassEntry(models.Model):
    """ Benchmark Definition Worker Pass"""
    definition = models.ForeignKey('benchmark.BenchmarkDefinitionEntry', related_name="worker_pass_definition")
    worker = models.ForeignKey('bluesteelworker.WorkerEntry', related_name='worker_pass_worker')
    allowed = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'Benchmark Definition Worker Pass id:{0} definition:{1} worker:{2} allowed:{3}'.format(
            self.id,
            self.definition.id,
            self.worker.id,
            self.allowed,
        )

    def as_object(self):
        """ Returns Benchmark Definition Worker Pass as an object"""
        obj = {}
        obj['id'] = self.id
        obj['definition'] = {}
        obj['definition']['id'] = self.definition.id
        obj['worker'] = {}
        obj['worker']['id'] = self.worker.id
        obj['worker']['name'] = self.worker.name
        obj['worker']['uuid'] = self.worker.uuid
        obj['allowed'] = self.allowed

        return obj
