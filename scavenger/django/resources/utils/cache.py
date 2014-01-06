#!/bin/env python
# -*- coding: utf-8 -*-
#
# Created on 16/05/2013

"""Module docstring

"""

__all__ = [
    'fix_key',
    'make_template_fragment_key',
]

import re
import hashlib

from django.utils.http import urlquote
from django.utils.encoding import smart_str


TEMPLATE_FRAGMENT_KEY_TEMPLATE = 'template.cache.%s.%s'


def fix_key(key):
    cache_key = re.sub(r'\s+', '-', key)
    cache_key = smart_str(cache_key)
    if len(cache_key) > 250:
        cache_key = cache_key[:200] + '-' + hashlib.new(cache_key).hexdigest()

    return cache_key


def make_template_fragment_key(fragment_name, vary_on=None):
    """Backport from Django-dev.
    Retrieve the cachekey for a template fragment

    :param fragment_name: Name of the template fragment
    :param vary_on: list of all additional arguments passed to the tag
    """
    if vary_on is None:
        vary_on = ()
    args = hashlib.md5(u':'.join([urlquote(var) for var in vary_on]))
    cache_key = 'template.cache.%s.%s' % (fragment_name, args.hexdigest())
    return cache_key
