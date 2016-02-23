""" Register your models here. """

from django.contrib import admin
from app.logic.mailing.models.StackedMailModel import StackedMailEntry

admin.site.register(StackedMailEntry)
