""" GitCommit model """

from django.db import models

class GitCommitEntry(models.Model):
    """ Git Commit """
    project = models.ForeignKey('gitrepo.GitProjectEntry', related_name='git_commit_project')
    commit_hash = models.CharField(max_length=40, default='0' * 40)
    author = models.ForeignKey('gitrepo.GitUserEntry', related_name='git_commit_author')
    author_date = models.DateTimeField()
    committer = models.ForeignKey('gitrepo.GitUserEntry', related_name='git_commit_committer')
    committer_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'Commit hash:{0}, name:{1}'.format(self.commit_hash, self.author.name)

