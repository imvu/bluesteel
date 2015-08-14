""" BlueSteelLayout model """

from django.db import models
from app.service.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.service.bluesteel.managers.BluesteelLayoutManager import BluesteelLayoutManager

class BluesteelLayoutEntry(models.Model):
    """ BlueSteel Layout """
    name = models.CharField(default='', max_length=50)
    archive = models.CharField(default='', max_length=50)
    collect_commits_path = models.CharField(default='', max_length=50)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    objects = BluesteelLayoutManager()

    def __unicode__(self):
        return u'Bluesteel Layout name:{0}'.format(
            self.name
        )

    def as_object(self):
        """ Returns a layout entry as an object """
        project_entries = BluesteelProjectEntry.objects.all().filter(layout_id=self.id).order_by('id')

        projects = []
        for entry in project_entries:
            projects.append(entry.as_object())

        obj = {}
        obj['name'] = self.name
        obj['archive'] = self.archive
        obj['collect_commits_path'] = self.collect_commits_path
        obj['id'] = self.id
        obj['projects'] = projects
        return obj

