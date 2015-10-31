""" Benchmark Admin """

from django.contrib import admin
from app.service.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.service.benchmark.models.BenchmarkExecutionModel import BenchmarkExecutionEntry

admin.site.register(BenchmarkDefinitionEntry)
admin.site.register(BenchmarkExecutionEntry)
