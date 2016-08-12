""" Request module """

# Disable warning for relative imports
# pylint: disable=W0403

import httplib
import urllib2
import cookielib
import Cookie
import json


class Session(object):
    """An HTTP session"""
    def __init__(self):
        cookie_jar = cookielib.CookieJar()
        self.opener = urllib2.build_opener(
            urllib2.HTTPCookieProcessor(cookie_jar),
            # urllib2.HTTPHandler(debuglevel=1)
        )
        self.headers = {}
        self.headers['X-CSRFToken'] = ''
        self.headers['Content-Type'] = 'application/json'

    def update_csrf_token(self, cookie_content):
        """ Updates csrf token if it is found on a cookie """
        if cookie_content == '':
            return

        cookie = Cookie.SimpleCookie(cookie_content)
        if cookie.get('csrftoken') != None:
            self.headers['X-CSRFToken'] = cookie['csrftoken'].value

    def make_request(self, request):
        """ makes a request and returns an object with the result """
        res = {}
        res['type'] = 'unknown'
        try:
            response = self.opener.open(request)
        except urllib2.HTTPError as error:
            res['content'] = error.read()
            res['cookie'] = ''
            res['succeed'] = False
        except urllib2.URLError as error:
            res['content'] = str(error)
            res['cookie'] = ''
            res['succeed'] = False
        except httplib.BadStatusLine as error:
            res['content'] = str(error)
            res['cookie'] = ''
            res['succeed'] = False
        else:
            res = Session.transform_content_to_response(response)
        return res

    def get(self, url, headers):
        """ Performs a GET to a url, with headers and using a opener with cookies """
        for key in self.headers:
            headers[key] = self.headers[key]

        request = urllib2.Request(url=url, data=None, headers=headers)
        res = self.make_request(request)
        self.update_csrf_token(res['cookie'])
        return res

    def post(self, url, headers, data):
        """ Performs a POST to a url, with headers and using a opener with cookies """
        for key in self.headers:
            headers[key] = self.headers[key]

        request = urllib2.Request(url=url, data=data, headers=headers)
        res = self.make_request(request)
        self.update_csrf_token(res['cookie'])
        return res

    @staticmethod
    def transform_content_to_response(response):
        """ Transform received data and packs it inside an envelope """
        res = {}
        info = response.info()

        res['cookie'] = response.headers.get('Set-Cookie')
        res['type'] = info.type

        if info.maintype == 'text':
            res['content'] = json.loads(response.read())
            res['succeed'] = True
            return res

        if info.type == 'application/zip':
            res['content'] = response.read()
            res['succeed'] = True
            return res

        res['content'] = ''
        res['succeed'] = False
        return res
