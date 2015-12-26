""" Admin file """

from django.contrib import admin
from app.logic.gitfeeder.models.FeedModel import FeedEntry

admin.site.register(FeedEntry)
