""" Presenter Urls file """

from django.conf.urls import patterns, url

# pylint: disable=C0103
urlpatterns = patterns(
    '',
    url(r'^view/$',
        'app.presenter.views.ViewMain.get_main'),

    url(r'^layout/edit/(?P<layout_id>\d+)/$',
        'app.presenter.views.ViewLayout.get_layout_editable'),
)
