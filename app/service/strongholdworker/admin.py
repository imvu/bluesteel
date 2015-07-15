""" Admin file """

from django.contrib import admin
from app.service.strongholdworker.models.WorkerModel import WorkerEntry

admin.site.register(WorkerEntry)
