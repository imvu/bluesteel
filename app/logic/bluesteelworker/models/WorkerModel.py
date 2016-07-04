""" Worker model """

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from app.logic.httpcommon import trans
import datetime

class WorkerEntry(models.Model):
    """ Worker Model """

    name = models.TextField(default='')
    uuid = models.TextField(default='')
    operative_system = models.TextField(default='')
    description = models.TextField(default='')
    user = models.ForeignKey(User, related_name='worker_user')
    git_feeder = models.BooleanField(default=False)
    max_feed_reports = models.IntegerField(default=100)
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
        obj['operative_system'] = self.operative_system
        obj['description'] = self.description
        obj['git_feeder'] = self.git_feeder
        obj['max_feed_reports'] = self.max_feed_reports
        obj['last_update'] = trans.to_date_obj(self.updated_at)
        obj['activity'] = (timezone.now() - self.updated_at) < datetime.timedelta(seconds=30)
        return obj
