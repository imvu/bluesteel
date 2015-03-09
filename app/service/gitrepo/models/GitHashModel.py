""" Git Hash model """

from django.db import models

class GitHashEntry(models.Model):
    """ Git Hash """
    project = models.ForeignKey('gitrepo.GitProjectEntry', related_name='git_hash_project')
    git_hash = models.CharField(max_length=40, default='0' * 40)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'Hash: {0}'.format(self.git_hash)
