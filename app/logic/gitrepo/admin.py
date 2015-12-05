""" Admin file """

from django.contrib import admin
from app.logic.gitrepo.models.GitBranchModel import GitBranchEntry
from app.logic.gitrepo.models.GitBranchMergeTargetModel import GitBranchMergeTargetEntry
from app.logic.gitrepo.models.GitBranchTrailModel import GitBranchTrailEntry
from app.logic.gitrepo.models.GitParentModel import GitParentEntry
from app.logic.gitrepo.models.GitCommitModel import GitCommitEntry
from app.logic.gitrepo.models.GitProjectModel import GitProjectEntry
from app.logic.gitrepo.models.GitUserModel import GitUserEntry
from app.logic.gitrepo.models.GitDiffModel import GitDiffEntry


# Register your models here.

admin.site.register(GitParentEntry)
admin.site.register(GitCommitEntry)
admin.site.register(GitBranchEntry)
admin.site.register(GitBranchMergeTargetEntry)
admin.site.register(GitBranchTrailEntry)
admin.site.register(GitUserEntry)
admin.site.register(GitDiffEntry)
admin.site.register(GitProjectEntry)
