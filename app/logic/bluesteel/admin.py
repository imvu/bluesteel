""" Admin file """

from django.contrib import admin
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.logic.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry

admin.site.register(BluesteelProjectEntry)
admin.site.register(BluesteelLayoutEntry)
