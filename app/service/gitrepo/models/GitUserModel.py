""" GitUser model """

from django.db import models

class GitUserEntry(models.Model):
    """ Git User """
    project = models.ForeignKey('gitrepo.GitProjectEntry', related_name='git_user_project')
    name = models.CharField(max_length=50, default='')
    email = models.EmailField(max_length=75)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'GitUser name:{0}, email:{1}'.format(self.name, self.email)
