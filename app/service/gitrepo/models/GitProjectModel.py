""" Git Project model """

from django.db import models
from django.utils import timezone
from app.service.gitrepo.models.GitBranchModel import GitBranchEntry

class GitProjectEntry(models.Model):
    """ Git Project """
    url = models.URLField(max_length=255)
    name = models.CharField(max_length=50, default='default-name')
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    fetched_at = models.DateTimeField(auto_now_add=True, default=timezone.now)

    def __unicode__(self):
        return u'GitProject {0} url:{1}'.format(self.id, self.url)

    def as_object(self):
        """ Return a GirProject as an object """
        branch_entries = GitBranchEntry.objects.all().filter(project=self.id).order_by('id')

        branches = []
        for branch in branch_entries:
            branches.append(branch.as_object())

        obj = {}
        obj['url'] = self.url
        obj['name'] = self.name
        obj['branches'] = branches
        return obj
