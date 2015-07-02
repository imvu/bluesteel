""" StringholdWorker Urls file """

from django.conf.urls import patterns, url

# pylint: disable=C0103
urlpatterns = patterns(
    '',

    url(r'^download/$',
        'app.service.strongholdworker.views.ViewsWorker.get_worker'),

    # [a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}
    #
    # Third group must start with a '4', and the forth with a 8,9,a,b
    # i.e: 00000000-0000-4000-a000-000000000000
    url(r'^worker/(?P<worker_uuid>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})/$',
        'app.service.strongholdworker.views.ViewsWorker.get_worker_info'),
)
