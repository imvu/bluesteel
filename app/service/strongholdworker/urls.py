""" StringholdWorker Urls file """

from django.conf.urls import patterns, url

# pylint: disable=C0103
urlpatterns = patterns(
    '',
    url(r'^worker/$',
        'app.service.strongholdworker.views.ViewsGitRepo.get_branch_list'),
)
