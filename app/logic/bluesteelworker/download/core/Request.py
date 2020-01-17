""" Request module """

# Disable warning for relative imports
# : disable=W0403

# Disable broad exception, I don't know now the exact exception of request.read()
# pylint: disable=W0703

import urllib
import http
import http.cookiejar as cookielib
import http.cookies as Cookie
import json


class Session():
    """An HTTP session"""
    def __init__(self):
        cookie_jar = cookielib.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(cookie_jar),
            # urllib.HTTPHandler(debuglevel=1)
        )
        self.headers = {}
        self.headers['X-CSRFToken'] = ''
        self.headers['Content-Type'] = 'application/json'

    def update_csrf_token(self, cookie_content):
        """ Updates csrf token if it is found on a cookie """
        if cookie_content == '':
            return

        cookie = Cookie.SimpleCookie(cookie_content)
        if cookie.get('csrftoken') is not None:
            self.headers['X-CSRFToken'] = cookie['csrftoken'].value

    def make_request(self, request):
        """ makes a request and returns an object with the result """
        res = {}
        res['type'] = 'unknown'
        try:
            response = self.opener.open(request)
        except urllib.error.HTTPError as error:
            res['content'] = error.read()
            res['cookie'] = ''
            res['succeed'] = False
        except urllib.error.URLError as error:
            res['content'] = str(error)
            res['cookie'] = ''
            res['succeed'] = False
        except http.client.BadStatusLine as error:
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

        request = urllib.request.Request(url=url, data=None, headers=headers)
        res = self.make_request(request)
        self.update_csrf_token(res['cookie'])
        return res

    def post(self, url, headers, data):
        """ Performs a POST to a url, with headers and using a opener with cookies """
        for key in self.headers:
            headers[key] = self.headers[key]

        request = urllib.request.Request(url=url, data=data, headers=headers)
        res = self.make_request(request)
        self.update_csrf_token(res['cookie'])
        return res

    @staticmethod
    def transform_content_to_response(response):
        """ Transform received data and packs it inside an envelope """
        res = {}
        info = response.info()

        res['cookie'] = response.headers.get('Set-Cookie')
        res['type'] = info.get_content_type()
        res['content'] = ''
        res['succeed'] = False

        if info.get_content_maintype() == 'text':
            try:
                data = json.loads(response.read())
            except Exception:
                return res

            res['content'] = data
            res['succeed'] = True
            return res

        if info.get_content_type() == 'application/zip':
            try:
                data = response.read()
            except Exception:
                return res

            res['content'] = data
            res['succeed'] = True
            return res

        return res
