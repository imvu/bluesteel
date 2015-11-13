""" BenchmarkExecution model """

from django.db import models

class BenchmarkExecutionEntry(models.Model):
    """ Benchmark Execution """

    READY = 0
    IN_PROGRESS = 1
    FINISHED = 2
    STATUS_TYPE = (
        (READY, 'Ready'),
        (IN_PROGRESS, 'In_Progress'),
        (FINISHED, 'Finished'),
    )

    definition = models.ForeignKey('benchmark.BenchmarkDefinitionEntry', related_name='benchmark_exec_definition')
    commit = models.ForeignKey('gitrepo.GitCommitEntry', related_name='benchmark_exec_commit')
    report = models.ForeignKey('commandrepo.CommandSetEntry', related_name='benchmark_exec_command_set')
    invalidated = models.BooleanField(default=False)
    revision_target = models.IntegerField(default=-1)
    status = models.IntegerField(choices=STATUS_TYPE, default=READY)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'Benchmark Execution id:{0}'.format(
            self.id
        )

    def as_object(self):
        """ Returns Benchmark execution as an object """
        obj = {}
        obj['definition'] = self.definition.as_object()
        obj['commit'] = self.commit.commit_hash
        obj['report'] = self.report.as_object()
        obj['invalidated'] = self.definition.revision != self.revision_target
        return obj




