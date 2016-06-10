""" Git Branch model """

from django.db import models

class GitBranchEntry(models.Model):
    """ Git Branch """
    project = models.ForeignKey('gitrepo.GitProjectEntry', related_name='git_branch_project')
    name = models.TextField(default='')
    commit = models.ForeignKey('gitrepo.GitCommitEntry', related_name='git_branch_commit')
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'Branch - id:{0} hash:{1}, name:{2}'.format(self.id, self.commit.commit_hash, self.name)

    def as_object(self):
        """ Returns the entry as an object """
        obj = {}
        obj['project'] = self.project.id
        obj['name'] = self.name
        obj['commit_hash'] = self.commit.commit_hash
        obj['order'] = self.order
        return obj
