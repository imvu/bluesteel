""" Worker model """

import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from app.logic.httpcommon import trans

# Window of time to considere if the has been activty with this worker.
# Now at 15 min.
ACTIVITY_TIME = 15 * 60

class WorkerEntry(models.Model):
    """ Worker Model """

    name = models.TextField(default='')
    uuid = models.TextField(default='')
    operative_system = models.TextField(default='')
    description = models.TextField(default='Edit this description!')
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
        obj['last_update'] = trans.to_date_obj(self.updated_at)
        obj['activity'] = (timezone.now() - self.updated_at) < datetime.timedelta(seconds=ACTIVITY_TIME)

        obj['max_feed_reports'] = {}
        obj['max_feed_reports']['current_value'] = self.max_feed_reports
        obj['max_feed_reports']['current_name'] = ''
        obj['max_feed_reports']['names'] = self.get_max_feed_reports_names_and_values()

        for val in obj['max_feed_reports']['names']:
            if val['current']:
                obj['max_feed_reports']['current_name'] = val['name']


        return obj

    def get_max_feed_reports_names_and_values(self):
        """ Returns names, values, and current for all the possible values of max feed reports """
        values = [
            {'name' : '10 Reports', 'reports' : 10},
            {'name' : '20 Reports', 'reports' : 20},
            {'name' : '30 Reports', 'reports' : 30},
            {'name' : '40 Reports', 'reports' : 40},
            {'name' : '50 Reports', 'reports' : 50},
            {'name' : '100 Reports', 'reports' : 100},
        ]

        for val in values:
            val['current'] = val['reports'] == self.max_feed_reports

        return values
