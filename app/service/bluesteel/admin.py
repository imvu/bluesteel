""" Admin file """

from django.contrib import admin
from app.service.bluesteel.models.BluesteelCommandModel import BluesteelCommandEntry
from app.service.bluesteel.models.BluesteelCommandSetModel import BluesteelCommandSetEntry
from app.service.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry

admin.site.register(BluesteelCommandEntry)
admin.site.register(BluesteelCommandSetEntry)
admin.site.register(BluesteelProjectEntry)
