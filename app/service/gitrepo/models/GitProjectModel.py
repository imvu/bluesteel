""" Git Project model """

from django.db import models
from django.utils import timezone

class GitProjectEntry(models.Model):
    """ Git Project """
    url = models.URLField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    fetched_at = models.DateTimeField(auto_now_add=True, default=timezone.now)

    def __unicode__(self):
        return u'GitProject {0} url:{1}'.format(self.id, self.url)
