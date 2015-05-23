""" Presenter views, main page functions """

from django.http import HttpResponse
from django.template import RequestContext, loader
# from app.service.bluesteel.models.BluesteelLayourModel import BluesteelLayourEntry


def get_main(request):
    """ Returns html for the main page """
    # layout_entries = BluesteelLayourEntry.objects.all()

    template = loader.get_template('presenter/main.html')
    context = RequestContext(
        request,
        {},
    )

    response = HttpResponse(template.render(context))
    return response
