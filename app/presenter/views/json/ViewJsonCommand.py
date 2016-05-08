""" Presenter json views, layout page functions """

from django.http import HttpResponse
from app.logic.commandrepo.models.CommandModel import CommandEntry
from app.logic.httpcommon import res
import json

def download_command_as_json(request, command_id):
    """ Retrieves a command by id and generates a file to be downloaded """
    if request.method == 'GET':
        comm = CommandEntry.objects.filter(id=command_id).first()

        json_response = {}

        if comm:
            json_response = comm.as_object()
        else:
            json_response['msg'] = 'Command with id {0} not found'.format(command_id)

        response = HttpResponse(
            json.dumps(json_response, indent=4, separators=(',', ': ')),
            content_type='application/json')

        response['Content-Disposition'] = 'attachment; filename=Command-{0}.json'.format(command_id)
        return response
    else:
        return res.get_only_get_allowed({})
