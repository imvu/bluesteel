""" StringholdWorker Urls file """

from django.conf.urls import patterns, url

# pylint: disable=C0103
urlpatterns = patterns(
    '',

    url(r'^download/$',
        'app.service.strongholdworker.views.ViewsWorker.get_worker'),
)
