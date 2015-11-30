""" BluesteelWorker Urls file """

from django.conf.urls import patterns, url

# pylint: disable=C0103
urlpatterns = patterns(
    '',

    url(r'^download/$',
        'app.service.bluesteelworker.views.ViewsWorker.get_worker'),

    # Using a UUID regex for a uuid3 version
    # [0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}
    url(r'^worker/(?P<worker_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        'app.service.bluesteelworker.views.ViewsWorker.get_worker_info'),

    url(r'^worker/create/',
        'app.service.bluesteelworker.views.ViewsWorker.create_worker_info'),

    url(r'^worker/login/',
        'app.service.bluesteelworker.views.ViewsWorker.login_worker_info'),

    url(r'^worker/(?P<worker_id>\d+)/update/activity/',
        'app.service.bluesteelworker.views.ViewsWorker.update_worker_activity'),
)
