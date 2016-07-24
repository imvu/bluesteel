""" Git Project model """

from django.db import models
from app.logic.gitrepo.models.GitBranchModel import GitBranchEntry
from app.logic.gitrepo.models.GitBranchMergeTargetModel import GitBranchMergeTargetEntry

class GitProjectEntry(models.Model):
    """ Git Project """
    url = models.URLField(max_length=255)
    name = models.CharField(max_length=50, default='default-name')
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    fetched_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'GitProject {0} url:{1}'.format(self.id, self.url)

    def as_object(self):
        """ Return a GirProject as an object """
        branch_entries = GitBranchEntry.objects.filter(project=self.id).order_by('id')

        branches = []
        for branch in branch_entries:
            obj = branch.as_object()

            merge_entry = GitBranchMergeTargetEntry.objects.filter(
                project=self.id,
                current_branch__commit__commit_hash=branch.commit.commit_hash
            ).first()

            if merge_entry:
                obj['merge_target'] = merge_entry.as_object()

            branches.append(obj)


        obj = {}
        obj['url'] = self.url
        obj['name'] = self.name
        obj['branches'] = branches
        return obj
