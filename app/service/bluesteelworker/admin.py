""" Admin file """

from django.contrib import admin
from app.service.bluesteelworker.models.WorkerModel import WorkerEntry

admin.site.register(WorkerEntry)
