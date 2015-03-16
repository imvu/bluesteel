""" GitFeeder Urls file """

from django.conf.urls import patterns, url

# pylint: disable=C0103
urlpatterns = patterns(
    '',
    url(r'^feed/commit/project/(?P<project_id>\d+)/$',
        'app.service.gitfeeder.views.ViewsGitFeed.post_commits'),
)
