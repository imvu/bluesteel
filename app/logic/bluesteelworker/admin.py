""" Admin file """

from django.contrib import admin
from app.logic.bluesteelworker.models.WorkerModel import WorkerEntry

admin.site.register(WorkerEntry)
