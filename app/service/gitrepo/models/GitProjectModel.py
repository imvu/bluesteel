""" Git Project model """

from django.db import models

class GitProjectEntry(models.Model):
    """ Git Project """
    url = models.URLField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'GitProject url:{0}'.format(self.url)
