""" FluctuationOverride model """

from django.db import models

class BenchmarkFluctuationOverrideEntry(models.Model):
    """ Fluctuation Override """
    definition = models.ForeignKey('benchmark.BenchmarkDefinitionEntry', related_name='fluctuation_override_definition')
    result_id = models.CharField(default='', max_length=255)
    override_value = models.IntegerField(default=0)
    ignore_fluctuation = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'Fluctuation Override id:{0}, definition:{1}, result_id:{2}, \
            ignore_fluctuation:{3} override_value:{4}'.format(
                self.id,
                self.definition.id,
                self.result_id,
                self.ignore_fluctuation,
                self.override_value,
            )
