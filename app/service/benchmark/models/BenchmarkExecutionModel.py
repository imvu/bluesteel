""" BenchmarkExecution model """

from django.db import models

class BenchmarkExecutionEntry(models.Model):
    """ Benchmark Execution """
    definition = models.ForeignKey('benchmark.BenchmarkDefinitionEntry', related_name='benchmark_exec_definition')
    commit = models.ForeignKey('gitrepo.GitCommitEntry', related_name='benchmark_exec_commit')
    report = models.ForeignKey('commandrepo.CommandSetEntry', related_name='benchmark_exec_command_set')
    invalidated = models.BooleanField(default=False)
    revision_target = models.IntegerField(default=-1)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'Benchmark Definition id:{0} name:{1}'.format(
            self.id,
            self.name,
        )

    def as_object(self):
        obj = {}
        obj['definition'] = self.definition.as_object()
        obj['commit'] = self.commit.commit_hash
        obj['report'] = self.report.as_object()
        obj['invalidated'] = self.definition.revision != self.revision_target
        return obj




