""" Git Branch Merge Target model """

from django.db import models

class GitBranchMergeTargetEntry(models.Model):
    """ Git Branch Merge Target """
    project = models.ForeignKey('gitrepo.GitProjectEntry', related_name='git_merge_project')
    current_branch = models.ForeignKey('gitrepo.GitBranchEntry', related_name='git_merge_current_branch')
    target_branch = models.ForeignKey('gitrepo.GitBranchEntry', related_name='git_merge_target_branch')
    fork_point = models.ForeignKey('gitrepo.GitCommitEntry', related_name='git_merge_target_fork')
    diff = models.ForeignKey('gitrepo.GitDiffEntry', null=True, related_name='git_merge_diff')
    invalidated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'MergeTarget - project:{0}, current branc:{1}, target branch:{2}'.format(
            self.project.id,
            self.current_branch.name,
            self.target_branch.name
        )

    def as_object(self):
        """ Returns Merge target as an object """
        obj = {}
        obj['current_branch'] = self.current_branch.as_object()
        obj['target_branch'] = self.target_branch.as_object()
        obj['fork_point'] = self.fork_point.as_object()
        return obj
