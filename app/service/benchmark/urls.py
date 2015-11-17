""" Benchmark Urls file """

from django.conf.urls import patterns, url

#pylint: disable=C0103
urlpatterns = patterns(
    '',
    url(r'^execution/acquire/$',
        'app.service.benchmark.views.ViewsBenchmark.acquire_benchmark_execution'),

)
