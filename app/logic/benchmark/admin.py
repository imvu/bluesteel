""" Benchmark Admin """

from django.contrib import admin
from app.logic.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.logic.benchmark.models.BenchmarkExecutionModel import BenchmarkExecutionEntry
from app.logic.benchmark.models.BenchmarkFluctuationOverrideModel import BenchmarkFluctuationOverrideEntry

admin.site.register(BenchmarkDefinitionEntry)
admin.site.register(BenchmarkExecutionEntry)
admin.site.register(BenchmarkFluctuationOverrideEntry)
