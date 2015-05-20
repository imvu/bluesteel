""" Presenter views, main page functions """

from django.http import HttpResponse
from django.conf import settings
from django.template import RequestContext, loader

def get_main(request):
    """ Returns html for the main page """
    template = loader.get_template('presenter/main.html')
    context = RequestContext(
        request,
        {},
    )

    response = HttpResponse(template.render(context))
    return response