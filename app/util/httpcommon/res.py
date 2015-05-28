""" Common code for response """

from django.http import HttpResponse
from django.template import RequestContext, loader
import json

def add_cross_origin_properties(http_request):
    """ Setup the required headers to allow cross origin requests """
    http_request["Access-Control-Allow-Origin"] = "*"
    http_request["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    http_request["Access-Control-Max-Age"] = "1000"
    http_request["Access-Control-Allow-Headers"] = "*"

def get_response(status, message, data):
    """ Creates a response with a predefined layout """
    msg = {}
    msg['status'] = status
    msg['message'] = message
    if data:
        msg['data'] = data
    response = HttpResponse(json.dumps(msg))
    add_cross_origin_properties(response)
    return response

def check_cross_origin_headers(self, response):
    self.assertEqual(response['Access-Control-Allow-Origin'], '*')
    self.assertEqual(response['Access-Control-Allow-Methods'], 'POST, GET, OPTIONS')
    self.assertEqual(response['Access-Control-Max-Age'], '1000')
    self.assertEqual(response['Access-Control-Allow-Headers'], '*')

def get_only_get_allowed(data):
    return get_response(400, 'Only GET allowed.', data)

def get_only_post_allowed(data):
    return get_response(400, 'Only POST allowed.', data)

def get_login_required(data):
    return get_response(401, 'Login required.', data)

def get_json_parser_failed(data):
    return get_response(406, 'Json parser failed.', data)

def get_schema_failed(data):
    return get_response(406, 'Schema failed.', data)

def get_template_data(request, template, data):
    template = loader.get_template(template)
    context = RequestContext(request, data)
    response = HttpResponse(template.render(context))
    return response
