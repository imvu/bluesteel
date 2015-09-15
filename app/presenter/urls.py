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

    url(r'^layout/(?P<layout_id>\d+)/add/project/$',
        'app.presenter.views.ViewLayout.add_default_project'),

    url(r'^layout/create/$',
        'app.presenter.views.ViewLayout.post_create_new_layout'),

    url(r'^project/(?P<project_id>\d+)/save/$',
        'app.presenter.views.ViewProject.save_project'),

    url(r'^project/(?P<project_id>\d+)/delete/$',
        'app.presenter.views.ViewProject.delete_project'),

    url(r'^workers/$',
        'app.presenter.views.ViewWorkers.get_workers'),

    url(r'^worker/(?P<worker_id>\d+)/report/all/$',
        'app.presenter.views.ViewWorkers.get_worker_reports'),
)
