""" Admin file """

from django.contrib import admin
from app.logic.gitfeeder.models.FeedModel import FeedEntry
from app.logic.commandrepo.controllers.CommandController import CommandController

def delete_all_feeds(self, request, queryset):
    """ Delete all the feeds with all of its associated commands """
    del queryset
    entries = FeedEntry.objects.all()

    for entry in entries:
        CommandController.delete_command_group_by_id(entry.command_group.id)
        entry.delete()

    self.message_user(request, "All Feed entries were deleted successfully.")

delete_all_feeds.short_description = "Delete All Feed Entries"

class FeedAdmin(admin.ModelAdmin):
    actions = [delete_all_feeds]

admin.site.register(FeedEntry, FeedAdmin)
