#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Created on Oct 9, 2012

import sys
import re
import logging

from django import http
from django.utils.cache import add_never_cache_headers
from django.views.debug import technical_500_response
from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse


logger = logging.getLogger('default.middleware')

######### REQUIRED LOGIN MIDDLEWARE CONFIGURATION
#TODO: Does not match an error 500 (not a url of course, and not in request)
LOGIN_EXEMPT_URLS = [
    r'favicon\.ico',
    r'404',
    r'403',
    r'500',
    r'504',
]


EXEMPT_URLS = [re.compile(settings.LOGIN_URL.rstrip('/'))]
EXEMPT_URLS += [re.compile(expr) for expr in LOGIN_EXEMPT_URLS]


class UserBasedExceptionMiddleware(object):

    """Display stacktrace of errors in production."""

    def process_exception(self, request, exception):
        """Process Exceptions"""
        if request.user.is_superuser:
            # or request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS:
            return technical_500_response(request, *sys.exc_info())


class RequiredLoginMiddleware(object):

    """
    Require Login middleware. If enabled, each Django-powered page will
    require authentication.

    If an anonymous user requests a page, he/she is redirected to the login
    page set by urls.py.
    """

    def process_request(self, request):
        """Process request

        :param request: HttpRequest
        """
        assert hasattr(request, 'user'), """The Login Required middleware
         requires authentication middleware to be installed. Edit your
         MIDDLEWARE_CLASSES setting to insert
         'django.contrib.auth.middlware.AuthenticationMiddleware'. If that doesn't
         work, ensure your TEMPLATE_CONTEXT_PROCESSORS setting includes
         'django.core.context_processors.auth'."""

        path = request.path_info

        if not request.user.is_authenticated() and \
                not any(m.search(path) for m in EXEMPT_URLS):
            # logger.warning("No user authenticated")
            return HttpResponseRedirect(reverse('login') +
                                        "?next={0}".format(request.path))


class NeverCacheMiddleware(object):

    """Adds never cache headers"""

    def process_response(self,  request, response):
        add_never_cache_headers(response)
        return response


try:
    XS_SHARING_ALLOWED_ORIGINS = settings.XS_SHARING_ALLOWED_ORIGINS
    XS_SHARING_ALLOWED_METHODS = settings.XS_SHARING_ALLOWED_METHODS
except AttributeError:
    XS_SHARING_ALLOWED_ORIGINS = '*'
    XS_SHARING_ALLOWED_METHODS = ['POST', 'GET', 'OPTIONS', 'PUT', 'DELETE']


#TODO: Add a regex of trusted sources

class XsSharing(object):
    """
        This middleware allows cross-domain XHR using the html5 postMessage API.

    from: https://gist.github.com/barrabinfc/426829


        Access-Control-Allow-Origin: http://foo.example
        Access-Control-Allow-Methods: POST, GET, OPTIONS, PUT, DELETE
    """
    def process_request(self, request):

        if 'HTTP_ACCESS_CONTROL_REQUEST_METHOD' in request.META:
            response = http.HttpResponse()
            response['Access-Control-Allow-Origin'] = XS_SHARING_ALLOWED_ORIGINS
            response['Access-Control-Allow-Methods'] = ",".join(
                XS_SHARING_ALLOWED_METHODS)

            return response

        return None

    def process_response(self, request, response):
        # Avoid unnecessary work
        if response.has_header('Access-Control-Allow-Origin'):
            return response

        response['Access-Control-Allow-Origin']  = XS_SHARING_ALLOWED_ORIGINS
        response['Access-Control-Allow-Methods'] = ",".join(
            XS_SHARING_ALLOWED_METHODS)

        return response

"""
    threadlocals middleware
    ~~~~~~~~~~~~~~~~~~~~~~~

    make the request object everywhere available (e.g. in model instance).

    based on: http://code.djangoproject.com/wiki/CookBookThreadlocalsAndUser

    and from https://github.com/jedie/django-tools/blob/master/django_tools/middlewares/ThreadLocal.py

    Put this into your settings:
    --------------------------------------------------------------------------
        MIDDLEWARE_CLASSES = (
            ...
            'junglebook.middlewares.ThreadLocal.ThreadLocalMiddleware',
            ...
        )
    --------------------------------------------------------------------------


    Usage:
    --------------------------------------------------------------------------
    from django_tools.middlewares import ThreadLocal

    # Get the current request object:
    request = ThreadLocal.get_current_request()

    # You can get the current user directy with:
    user = ThreadLocal.get_current_user()
    --------------------------------------------------------------------------

    :copyleft: 2009-2011 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from threading import local


_thread_locals = local()


def get_current_request():
    """ returns the request object for this thead """
    return getattr(_thread_locals, "request", None)


def get_current_user():
    """ returns the current user, if exist, otherwise returns None """
    request = get_current_request()
    if request:
        return getattr(request, "user", None)


class ThreadLocalMiddleware(object):
    """ Simple middleware that adds the request object in thread local
    storage."""
    def process_request(self, request):
        _thread_locals.request = request