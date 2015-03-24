""" GitRepo Urls file """

from django.conf.urls import patterns, url

# pylint: disable=C0103
urlpatterns = patterns(
    '',
    url(r'^branch/all/project/(?P<project_id>\d+)/$',
        'app.service.gitrepo.views.ViewsGitRepo.get_branch_list'),

    url(r'^branch/merge/target/project/(?P<project_id>\d+)/$',
        'app.service.gitrepo.views.ViewsBranchMergeTarget.set_branch_merge_target'),
)
