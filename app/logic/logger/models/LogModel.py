""" Log model """

from django.db import models
from django.contrib.auth.models import User

class LogEntry(models.Model):
    """ Log entry """

    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4
    LOG_TYPE = (
        (DEBUG, 'Debug'),
        (INFO, 'Info'),
        (WARNING, 'Warning'),
        (ERROR, 'Error'),
        (CRITICAL, 'Critical'),
    )

    user = models.ForeignKey(User, related_name='log_user', blank=True, null=True)
    log_type = models.IntegerField(choices=LOG_TYPE, default=INFO)
    message = models.TextField(default='')
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'Log:{0}, {1}'.format(self.log_type, self.message)

    def as_object(self):
        """ Returns the log entry as an object """
        obj = {}
        obj['type'] = self.log_type
        obj['message'] = self.message

        return obj

    @staticmethod
    def debug(user, message):
        """ DEBUG log level entry """
        log_user = user
        if user.is_anonymous():
            log_user = None

        LogEntry.objects.create(
            user=log_user,
            log_type=LogEntry.DEBUG,
            message=message
        )

    @staticmethod
    def info(user, message):
        """ INFO log level entry """
        log_user = user
        if user.is_anonymous():
            log_user = None

        LogEntry.objects.create(
            user=log_user,
            log_type=LogEntry.INFO,
            message=message
        )

    @staticmethod
    def warning(user, message):
        """ WARNING log level entry """
        log_user = user
        if user.is_anonymous():
            log_user = None

        LogEntry.objects.create(
            user=log_user,
            log_type=LogEntry.WARNING,
            message=message
        )

    @staticmethod
    def error(user, message):
        """ ERROR log level entry """
        log_user = user
        if user.is_anonymous():
            log_user = None

        LogEntry.objects.create(
            user=log_user,
            log_type=LogEntry.ERROR,
            message=message
        )

    @staticmethod
    def critical(user, message):
        """ CRITICAL log level entry """
        log_user = user
        if user.is_anonymous():
            log_user = None

        LogEntry.objects.create(
            user=log_user,
            log_type=LogEntry.CRITICAL,
            message=message
        )
