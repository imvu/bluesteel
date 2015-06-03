""" Bluesteel Urls file """

from django.conf.urls import patterns, url

# pylint: disable=C0103
urlpatterns = patterns(
    '',

    url(r'^layout/create/$',
        'app.service.bluesteel.views.ViewBluesteel.post_create_new_layout'),
)
