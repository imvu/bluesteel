""" Admin file """

from django.contrib import admin
from app.logic.commandrepo.models.CommandResultModel import CommandResultEntry
from app.logic.commandrepo.models.CommandModel import CommandEntry
from app.logic.commandrepo.models.CommandSetModel import CommandSetEntry
from app.logic.commandrepo.models.CommandGroupModel import CommandGroupEntry

admin.site.register(CommandResultEntry)
admin.site.register(CommandEntry)
admin.site.register(CommandSetEntry)
admin.site.register(CommandGroupEntry)
