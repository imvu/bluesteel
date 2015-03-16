""" Admin file """

from django.contrib import admin
from app.service.gitrepo.models.GitHashModel import GitHashEntry
from app.service.gitrepo.models.GitBranchModel import GitBranchEntry
from app.service.gitrepo.models.GitBranchTrailModel import GitBranchTrailEntry
from app.service.gitrepo.models.GitParentModel import GitParentEntry
from app.service.gitrepo.models.GitCommitModel import GitCommitEntry
from app.service.gitrepo.models.GitProjectModel import GitProjectEntry
from app.service.gitrepo.models.GitUserModel import GitUserEntry
from app.service.gitrepo.models.GitDiffModel import GitDiffEntry


# Register your models here.

admin.site.register(GitHashEntry)
admin.site.register(GitParentEntry)
admin.site.register(GitCommitEntry)
admin.site.register(GitBranchEntry)
admin.site.register(GitBranchTrailEntry)
admin.site.register(GitUserEntry)
admin.site.register(GitDiffEntry)
admin.site.register(GitProjectEntry)
