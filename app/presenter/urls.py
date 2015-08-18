""" Presenter Urls file """

from django.conf.urls import patterns, url

# pylint: disable=C0103
urlpatterns = patterns(
    '',
    url(r'^view/$',
        'app.presenter.views.ViewMain.get_main'),

    url(r'^layout/edit/(?P<layout_id>\d+)/$',
        'app.presenter.views.ViewLayout.get_layout_editable'),

    url(r'^layout/(?P<layout_id>\d+)/save/$',
        'app.presenter.views.ViewLayout.save_layout'),

    url(r'^layout/create/$',
        'app.presenter.views.ViewLayout.post_create_new_layout'),

    url(r'^project/(?P<project_id>\d+)/save/$',
        'app.presenter.views.ViewProject.save_project'),
)
