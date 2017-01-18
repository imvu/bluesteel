""" Benchmark Admin """

from django.contrib import admin
from app.logic.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.logic.benchmark.models.BenchmarkDefinitionWorkerPassModel import BenchmarkDefinitionWorkerPassEntry
from app.logic.benchmark.models.BenchmarkExecutionModel import BenchmarkExecutionEntry
from app.logic.benchmark.models.BenchmarkFluctuationOverrideModel import BenchmarkFluctuationOverrideEntry

admin.site.register(BenchmarkDefinitionEntry)
admin.site.register(BenchmarkDefinitionWorkerPassEntry)
admin.site.register(BenchmarkFluctuationOverrideEntry)


class BenchmarkExecutionAdmin(admin.ModelAdmin):
    list_filter = ['commit__author__name', 'commit__commit_hash']

admin.site.register(BenchmarkExecutionEntry, BenchmarkExecutionAdmin)
