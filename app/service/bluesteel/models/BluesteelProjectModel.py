""" BlueSteelProject model """

from django.db import models
from app.service.bluesteel.models.BluesteelCommandSetModel import BluesteelCommandSetEntry

class BluesteelProjectEntry(models.Model):
    """ BlueSteel Project """
    layout = models.ForeignKey('bluesteel.BluesteelLayoutEntry', related_name='bluesteel_layout')
    archive = models.CharField(default='', max_length=50)
    name = models.CharField(default='', max_length=50)
    git_project = models.ForeignKey('gitrepo.GitProjectEntry', related_name='bluesteel_git_project')
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'Bluesteel Project layout:{0}, archive:{1}, name:{2}, git_project{3}'.format(
            self.layout.name,
            self.archive,
            self.name,
            self.git_project.id
        )

    def as_object(self):
        """ Returns a project as an object """
        obj = {}
        obj['name'] = self.name
        obj['archive'] = self.archive
        obj['git_project'] = {}
        obj['git_project']['name'] = self.git_project.name
        obj['git_project']['id'] = self.git_project.id
        obj['command_sets'] = []

        comm_set_entries = BluesteelCommandSetEntry.objects.all().filter(
            bluesteel_project=self.id
        ).order_by('command_set_type')

        for comm_set in comm_set_entries:
            obj['command_sets'].append(comm_set.as_object())

        return obj
