#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Created on 18/03/2013

"""Module docstring

"""

__all__ = [
    'BaseAjaxHttpResponse',
    'AjaxHttpResponse',
]

from django.http import HttpResponse
from django.utils import simplejson


class BaseAjaxHttpResponse(HttpResponse):
    def __init__(self, data):
        super(BaseAjaxHttpResponse, self).__init__(
            simplejson.dumps(data),
            content_type='application/json')


class AjaxHttpResponse(BaseAjaxHttpResponse):
    def __init__(self, success=True, errors=dict(), extra_message=None):
        super(AjaxHttpResponse, self).__init__(dict(success=success,
                                                    errors=errors,
                                                    extra_message=extra_message)
                                               )
