""" Git Branch Trail model """

from django.db import models

class GitBranchTrailEntry(models.Model):
    """ Git Branch Trail """
    project = models.ForeignKey('gitrepo.GitProjectEntry', related_name='git_trail_project')
    branch = models.ForeignKey('gitrepo.GitBranchEntry', related_name='git_trail_branch')
    commit = models.ForeignKey('gitrepo.GitCommitEntry', related_name='git_trail_commit')
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'Trail - project:{0}, name:{1}, commit:{2}, order:{3}'.format(
            self.project.id,
            self.branch.name,
            self.commit.commit_hash,
            self.order
        )
