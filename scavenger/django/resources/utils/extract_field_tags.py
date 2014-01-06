#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Created on Nov 12, 2012

"""
Extrac specific fields for templates and forms
"""

import re

from django import template
from django.contrib.auth.models import User

register = template.Library()


@register.filter(name='verbose_name') 
def verbose_name(instance, arg): 
    return instance._meta.get_field(arg).verbose_name


@register.filter(name='queryset_verbose_name') 
def get_queryset_field_verbose_name(queryset, arg):
    return queryset.model._meta.get_field(arg).verbose_name


@register.filter
def initialize_name(text):
    sep = re.compile( r'\s|s' )
    list_name = sep.split(text)
    return '.'.join([name.capitalize()[0] for name in list_name])


@register.filter
def nice_name(username):
    """Example::

        Hi, {{ user|nice_name }}
    """
    try:
        user = User.objects.get(username=username)
        name = user.get_full_name() or username
    except User.DoesNotExist:
        name = ""

    return name
