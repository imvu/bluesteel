""" FluctuationOverride model """

from django.db import models

class BenchmarkFluctuationOverrideEntry(models.Model):
    """ Fluctuation Override """
    definition = models.ForeignKey('benchmark.BenchmarkDefinitionEntry', related_name='fluctuation_override_definition')
    result_id = models.CharField(default='', max_length=32)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'Fluctuation Override id:{0}, definition:{1}, result_id:{2}'.format(
            self.id,
            self.definition.id,
            self.result_id
        )
