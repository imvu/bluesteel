""" Admin file """

from django.contrib import admin
from app.util.commandrepo.models.CommandModel import CommandEntry
from app.util.commandrepo.models.CommandSetModel import CommandSetEntry
from app.util.commandrepo.models.CommandReportModel import CommandReportEntry

admin.site.register(CommandEntry)
admin.site.register(CommandSetEntry)
admin.site.register(CommandReportEntry)
