#!/bin/env python
# -*- coding: utf-8 -*-
#
# Created on 18/06/2013

"""Invalidate the template cache"""

__all__ = [
    'reset_cache',
]

from hashlib import md5

from django.template import Library, Node
from django.core.cache import cache
from django.utils.http import urlquote
from django.template import TemplateSyntaxError

from .cache import make_template_fragment_key

register = Library()


class InvalidateTemplateCacheNode(Node):

    """Node to invalidate fragment cache"""

    def __init__(self, fragment_name, *args):
        self.fragment_name = fragment_name
        self.variables = []
        self.variables.append(args)

    def render(self, context):
        """Render context

        :param context: Rendered context
        """
        cache_key = make_template_fragment_key(self.fragment_name,
                                               self.variables)
        if cache.get(cache_key):
            cache.delete(cache_key)

        return ''


def reset_cache(parser, token):
    """This will reset the template cache for a given set of arguments

    Usage::

        {% load reset_cache %}
        {% if [condition] %}
            {% reset_cache [fragment_name] %}
        {% endif %}


    This tag also supports varying by a list of arguments::

        {% load reset_cache %}
        {% if [condition] %}
            {% reset_cache [fragment_name] [var1] [var2] ..  %}
        {% endif %}


    Which follows the built-in cache template tag structure

        {% load cache %}
        {% cache [expire_time] [fragment_name] %}
            .. some expensive processing ..
        {% endcache %}

        {% load cache %}
        {% cache [expire_time] [fragment_name] [var1] [var2] .. %}
            .. some expensive processing ..
        {% endcache %}

    Note that the reset_cache doesn't pass the [expire_time] variable
    """

    tokens = token.contents.split()
    if len(tokens) < 2:
        raise TemplateSyntaxError("reset_cache tag requires at least one "
                                  "argument.")
    return InvalidateTemplateCacheNode(tokens[1], tokens[2:])


register.tag('reset_cache', reset_cache)