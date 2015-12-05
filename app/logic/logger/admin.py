""" Admin file """

from django.contrib import admin
from app.logic.logger.models.LogModel import LogEntry

admin.site.register(LogEntry)
