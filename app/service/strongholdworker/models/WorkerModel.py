""" Worker model """

from django.db import models

class WorkerEntry(models.Model):
    """ Worker Model """

    name = models.TextField(default='')
    uuid = models.TextField(default='')
    description = models.TextField(default='')
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'Worker:{0}, name:{1}, uuid:{2}'.format(self.id, self.name, self.uuid)

    def as_object(self):
        """ Returns the entry as an object """
        obj = {}
        obj['id'] = self.id
        obj['name'] = self.name
        obj['uuid'] = self.uuid
        obj['description'] = self.description
        return obj
