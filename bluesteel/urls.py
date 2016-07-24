""" Urls file """

from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView
from django.conf import settings
admin.autodiscover()

# pylint: disable=C0103
urlpatterns = [
    # Examples:
    # url(r'^$', 'rowpow.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/',
        include(admin.site.urls)),

    url(r'^main/',
        include('app.presenter.urls')),

    url(r'^$',
        RedirectView.as_view(url='main/view/')),
]
