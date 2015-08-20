""" BlueSteelProject model """

from django.db import models
from app.service.bluesteel.managers.BluesteelProjectManager import BluesteelProjectManager

class BluesteelProjectEntry(models.Model):
    """ BlueSteel Project """
    name = models.CharField(default='', max_length=50)
    order = models.IntegerField(default=0)
    layout = models.ForeignKey('bluesteel.BluesteelLayoutEntry', related_name='bluesteel_layout')
    command_group = models.ForeignKey('commandrepo.CommandGroupEntry', related_name='bluesteel_command_group')
    git_project = models.ForeignKey('gitrepo.GitProjectEntry', related_name='bluesteel_git_project')
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    objects = BluesteelProjectManager()

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
        obj['order'] = self.order
        obj['git_project'] = self.git_project.as_object()
        obj['command_group'] = self.command_group.as_object()

        return obj
