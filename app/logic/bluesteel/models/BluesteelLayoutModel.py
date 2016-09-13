""" BlueSteelLayout model """

from django.db import models
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry

class BluesteelLayoutEntry(models.Model):
    """ BlueSteel Layout """
    name = models.CharField(default='', max_length=50)
    active = models.BooleanField(default=False)
    project_index_path = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'Bluesteel Layout name:{0}'.format(
            self.name
        )

    def as_object(self):
        """ Returns a layout entry as an object """
        project_entries = BluesteelProjectEntry.objects.filter(layout_id=self.id).order_by('id')

        projects = []
        for entry in project_entries:
            projects.append(entry.as_object())

        obj = {}
        obj['id'] = self.id
        obj['name'] = self.name
        obj['uuid'] = self.get_uuid()
        obj['active'] = self.active
        obj['project_index_path'] = self.project_index_path
        obj['id'] = self.id
        obj['projects'] = projects
        return obj

    def get_uuid(self):
        return 'archive-{0}'.format(self.id)

    def clamp_project_index_path(self):
        project_count = BluesteelProjectEntry.objects.filter(layout_id=self.id).count()

        self.project_index_path = max(0, min(self.project_index_path, project_count - 1))
        self.save()

    def check_active_state(self):
        project_count = BluesteelProjectEntry.objects.filter(layout_id=self.id).count()

        if project_count == 0 or self.project_index_path >= project_count:
            self.active = False
            self.save()
