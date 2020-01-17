""" BlueSteelProject model """

from django.db import models
from django.db.models import signals
from django.dispatch.dispatcher import receiver
from app.logic.commandrepo.models.CommandGroupModel import CommandGroupEntry
from app.logic.gitrepo.controllers.GitController import GitController

class BluesteelProjectEntry(models.Model):
    """ BlueSteel Project """
    name = models.CharField(default='', max_length=50)
    order = models.IntegerField(default=0)
    layout = models.ForeignKey('bluesteel.BluesteelLayoutEntry', related_name='bluesteel_layout')
    command_group = models.ForeignKey('commandrepo.CommandGroupEntry', related_name='bluesteel_command_group')
    git_project = models.ForeignKey('gitrepo.GitProjectEntry', related_name='bluesteel_git_project')
    git_project_folder_search_path = models.CharField(default='.', max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'Bluesteel Project layout:{0}, name:{1}, git_project{2}'.format(
            self.layout.name,
            self.name,
            self.git_project.id
        )

    def as_object(self):
        """ Returns a project as an object """
        obj = {}
        obj['id'] = self.id
        obj['name'] = self.name
        obj['uuid'] = self.get_uuid()
        obj['order'] = self.order
        obj['git_project'] = self.git_project.as_object()
        obj['git_project_folder_search_path'] = self.git_project_folder_search_path
        obj['command_group'] = self.command_group.as_object()

        return obj

    def get_uuid(self):
        return 'project-{0}'.format(self.id)

    def wipe_data(self):
        """ Wipe data associated with this project """
        GitController.wipe_project_data(self.git_project)


@receiver(models.signals.post_delete)
def bluesteel_project_entry_post_delete(sender, instance, **kwargs):
    """ This function will delete the command_group on any delete of this model """
    del kwargs
    if isinstance(instance, BluesteelProjectEntry) and (sender == BluesteelProjectEntry):
        signals.post_delete.disconnect(bluesteel_project_entry_post_delete, sender=BluesteelProjectEntry)
        try:
            if instance.command_group and instance.command_group.id is not None:
                instance.command_group.delete()
        except CommandGroupEntry.DoesNotExist:
            pass

        signals.post_delete.connect(bluesteel_project_entry_post_delete, sender=BluesteelProjectEntry)
