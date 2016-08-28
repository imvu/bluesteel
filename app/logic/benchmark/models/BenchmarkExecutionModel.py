""" BenchmarkExecution model """

import json
from django.db import models
from django.db.models import signals
from django.dispatch.dispatcher import receiver
from app.logic.commandrepo.models.CommandModel import CommandEntry
from app.logic.commandrepo.models.CommandSetModel import CommandSetEntry
from app.logic.commandrepo.models.CommandResultModel import CommandResultEntry

class BenchmarkExecutionEntry(models.Model):
    """ Benchmark Execution """

    READY = 0
    IN_PROGRESS = 1
    FINISHED = 2
    FINISHED_WITH_ERRORS = 3
    STATUS_TYPE = (
        (READY, 'Ready'),
        (IN_PROGRESS, 'In_Progress'),
        (FINISHED, 'Finished'),
        (FINISHED_WITH_ERRORS, 'Finished_With_Errors'),
    )

    definition = models.ForeignKey('benchmark.BenchmarkDefinitionEntry', related_name='benchmark_exec_definition')
    commit = models.ForeignKey('gitrepo.GitCommitEntry', related_name='benchmark_exec_commit')
    worker = models.ForeignKey('bluesteelworker.WorkerEntry', related_name='benchmark_exec_worker', null=True)
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
        obj['id'] = self.id
        obj['definition'] = self.definition.as_object()
        obj['commit'] = self.commit.commit_hash
        obj['worker'] = self.worker.as_object()
        obj['report'] = self.report.as_object()
        obj['invalidated'] = self.is_invalidated()
        obj['status'] = {}
        obj['status']['index'] = self.status
        obj['status']['name'] = self.STATUS_TYPE[obj['status']['index']][1]
        return obj


    def is_invalidated(self):
        """ Returns true if Benchmark execution is invalidated """
        return self.definition.revision != self.revision_target or self.invalidated

    def get_benchmark_results(self):
        """ Returns all the results for a given benchmark flattened on a list """
        results = []

        com_list = CommandEntry.objects.filter(command_set__id=self.report.id).order_by('order')
        for com_entry in com_list:
            result = CommandResultEntry.objects.filter(command_id=com_entry.id).first()
            if result:
                res = json.loads(result.out)

                for exec_item in res:
                    bench_res = {}
                    bench_res['id'] = exec_item['id']
                    bench_res['visual_type'] = exec_item['visual_type']
                    bench_res['data'] = exec_item['data']

                    if exec_item['visual_type'] == 'vertical_bars':
                        bench_res['average'] = BenchmarkExecutionEntry.get_average(exec_item['data'])

                    results.append(bench_res)

        return results


    @staticmethod
    def get_average(vector):
        """ Returns the average of a vector values """
        average = 0.0
        for value in vector:
            average += float(value)
        return average / float(len(vector))

@receiver(models.signals.post_delete)
def benchmark_exec_entry_post_delete(sender, instance, **kwargs):
    """ This function will delete the report on any delete of this model """
    del kwargs
    if isinstance(instance, BenchmarkExecutionEntry) and (sender == BenchmarkExecutionEntry):
        signals.post_delete.disconnect(benchmark_exec_entry_post_delete, sender=BenchmarkExecutionEntry)
        try:
            if instance.report and instance.report.id != None:
                instance.report.delete()
        except CommandSetEntry.DoesNotExist:
            pass

        signals.post_delete.connect(benchmark_exec_entry_post_delete, sender=BenchmarkExecutionEntry)
