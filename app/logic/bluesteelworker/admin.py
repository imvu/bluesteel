""" Admin file """

from django.contrib import admin
from app.logic.bluesteelworker.models.WorkerModel import WorkerEntry
from app.logic.bluesteelworker.models.WorkerFilesHashModel import WorkerFilesHashEntry

admin.site.register(WorkerEntry)
admin.site.register(WorkerFilesHashEntry)
