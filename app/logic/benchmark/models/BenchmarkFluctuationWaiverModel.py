""" FluctuationWaiver model """

from django.db import models

class BenchmarkFluctuationWaiverEntry(models.Model):
    """ Fluctuation Waiver """
    git_user = models.ForeignKey('gitrepo.GitUserEntry', related_name='fluctuation_waiver_git_project')
    notification_allowed = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'Fluctuation Waiver id:{0}, git_user:{2},{3}, notification_allowed:{4}'.format(
            self.id,
            self.git_user.name,
            self.git_user.email,
            self.notification_allowed,
        )
