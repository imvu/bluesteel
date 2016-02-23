""" StackedMail model """

from django.db import models

class StackedMailEntry(models.Model):
    """ Mail to be sent """
    sender = models.EmailField()
    receiver = models.EmailField()
    title = models.TextField(default='')
    content = models.TextField(default='')
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)

    def __unicode__(self):
        return u'Title: {0}'.format(self.title)

    def get_email_as_data(self):
        """ Returns data to feed send_mass_mail """
        data = []
        data.append(self.title)
        data.append(self.content)
        data.append(self.sender)
        data.append([self.receiver])
        return data
