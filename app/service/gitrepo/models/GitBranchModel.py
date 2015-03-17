""" Git Branch model """

from django.db import models

class GitBranchEntry(models.Model):
    """ Git Branch """
    project = models.ForeignKey('gitrepo.GitProjectEntry', related_name='git_branch_project')
    name = models.TextField(default='')
    commit_hash = models.ForeignKey('gitrepo.GitHashEntry', related_name='git_branch_hash')
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'Branch:{0}, name:{1}'.format(self.commit_hash.git_hash, self.name)

    def as_object(self):
        """ Returns the entry as an object """
        obj = {}
        obj['project'] = self.project.id
        obj['name'] = self.name
        obj['commit_hash'] = self.commit_hash.git_hash
        return obj
