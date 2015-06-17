""" Bluesteel Urls file """

from django.conf.urls import patterns, url

# pylint: disable=C0103
urlpatterns = patterns(
    '',
    url(r'^layout/all/urls/$',
        'app.service.bluesteel.views.ViewBluesteel.get_all_layouts_urls'),

    url(r'^layout/(?P<layout_id>\d+)/$',
        'app.service.bluesteel.views.ViewBluesteel.get_layout'),
)
