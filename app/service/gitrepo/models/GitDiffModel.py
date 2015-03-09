""" Git Diff model """

from django.db import models

class GitDiffEntry(models.Model):
    """ Git Diff """
    project = models.ForeignKey('gitrepo.GitProjectEntry', related_name='git_diff_project')
    content = models.TextField(default='')
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'Diff:{0}'.format(self.id)
