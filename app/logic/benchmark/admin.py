""" Benchmark Admin """

from django.contrib import admin
from app.logic.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.logic.benchmark.models.BenchmarkExecutionModel import BenchmarkExecutionEntry

admin.site.register(BenchmarkDefinitionEntry)
admin.site.register(BenchmarkExecutionEntry)
