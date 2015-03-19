""" Git Parent model """

from django.db import models

class GitParentEntry(models.Model):
    """ Git Parent """
    project = models.ForeignKey('gitrepo.GitProjectEntry', related_name='git_parent_project')
    parent = models.ForeignKey('gitrepo.GitCommitEntry', related_name='git_parent_commit')
    son = models.ForeignKey('gitrepo.GitCommitEntry', related_name='git_son_commit')
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'Parent:{0}, Son:{1}'.format(self.parent.commit_hash, self.son.commit_hash)
