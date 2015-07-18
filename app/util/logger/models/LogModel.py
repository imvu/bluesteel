""" Log model """

from django.db import models

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
    def debug(message):
        LogEntry.objects.create(
            log_type=LogEntry.DEBUG,
            message=message
        )

    @staticmethod
    def info(message):
        LogEntry.objects.create(
            log_type=LogEntry.INFO,
            message=message
        )

    @staticmethod
    def warning(message):
        LogEntry.objects.create(
            log_type=LogEntry.WARNING,
            message=message
        )

    @staticmethod
    def error(message):
        LogEntry.objects.create(
            log_type=LogEntry.ERROR,
            message=message
        )

    @staticmethod
    def critical(message):
        LogEntry.objects.create(
            log_type=LogEntry.CRITICAL,
            message=message
        )
