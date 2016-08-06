""" Worker files hash model """

from django.db import models

class WorkerFilesHashEntry(models.Model):
    """ Worker Files Hash Model """

    files_hash = models.TextField(default='')
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'WorkerFilesHash:{0}'.format(self.files_hash)

    def as_object(self):
        """ Returns the entry as an object """
        obj = {}
        obj['id'] = self.id
        obj['files_hash'] = self.files_hash
        return obj
