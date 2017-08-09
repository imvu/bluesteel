""" Benchmark Admin """

from django.contrib import admin
from app.logic.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.logic.benchmark.models.BenchmarkDefinitionWorkerPassModel import BenchmarkDefinitionWorkerPassEntry
from app.logic.benchmark.models.BenchmarkExecutionModel import BenchmarkExecutionEntry
from app.logic.benchmark.models.BenchmarkFluctuationOverrideModel import BenchmarkFluctuationOverrideEntry
from app.logic.benchmark.controllers.BenchmarkExecutionController import BenchmarkExecutionController

admin.site.register(BenchmarkDefinitionEntry)
admin.site.register(BenchmarkDefinitionWorkerPassEntry)
admin.site.register(BenchmarkFluctuationOverrideEntry)

def delete_all_benchmark_executions(self, request, queryset):
    """ Deletes all the Benchmark Executions with all its associated commands """
    del queryset
    entries = BenchmarkDefinitionEntry.objects.all()

    for entry in entries:
        BenchmarkExecutionController.delete_benchmark_executions(entry)

    self.message_user(request, "All Benchmark executions were deleted successfully.")

delete_all_benchmark_executions.short_description = "Delete All Benchmark Executions"

class BenchmarkExecutionAdmin(admin.ModelAdmin):
    list_filter = ['commit__author__name', 'commit__commit_hash']
    actions = [delete_all_benchmark_executions]

admin.site.register(BenchmarkExecutionEntry, BenchmarkExecutionAdmin)
