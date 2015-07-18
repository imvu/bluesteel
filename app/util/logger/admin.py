""" Admin file """

from django.contrib import admin
from app.util.logger.models.LogModel import LogEntry

admin.site.register(LogEntry)
