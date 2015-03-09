""" Git Parent model """

from django.db import models

class GitParentEntry(models.Model):
    """ Git Parent """
    project = models.ForeignKey('gitrepo.GitProjectEntry', related_name='git_parent_project')
    parent = models.ForeignKey('gitrepo.GitHashEntry', related_name='git_parent_hash')
    son = models.ForeignKey('gitrepo.GitHashEntry', related_name='git_son_hash')
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'Parent:{0}, Son:{1}'.format(self.parent, self.son)
