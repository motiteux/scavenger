#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Created on 06/01/2014

"""
Module doc
"""

import delorean

from django import template
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext as _
from django.conf import settings
from django.core.cache import cache


register = template.Library()

TIME_SHIFT = getattr(config, "DASHBOARD_MAX_SHIFT", 7)
ZUR_TZ = settings.TIME_ZONE
NOW = delorean.now


@register.filter
def join_with_commas(obj_list):
    """Takes a list of objects and returns their unicode representations,
    seperated by commas and with 'and' between the penultimate and final items
    For example, for a list of fruit objects:
    [<Fruit: apples>,<Fruit: oranges>,<Fruit: pears>] -> 'apples, oranges and pears'

    :param obj_list: List of object with __unicode__
    """
    if not len(obj_list):
        return
    len_list = len(obj_list)
    if len_list == 1:
        return u"%s" % obj_list[0]
    else:
        return u", ".join(obj for obj in obj_list[:len_list-1]) + u" " + _(u"and") + u" " + smart_unicode(obj_list[len_list-1])


@register.filter
def template_exists(template_name):
    """Return a boolean on the existence of the input template

    :param template_name: name of the template to test
    :return: True or False
    """
    try:
        template.loader.find_template(template_name)
        return True
    except template.loader.TemplateDoesNotExist:
        return False


def get_exc_str(bClear=False):
    """Handling PrettyPrint of Tracebacks.

    :param bClear: Boolean, Clear global information for further risen
        exceptions
    """
    import sys
    import traceback

    x = sys.exc_info()

    if not x[0]:
        return "No Python exception"
    out = "%s/%s/%s" % (str(x[0]), str(traceback.extract_tb(x[2])), str(x[1]))
    if bClear:
        sys.exc_clear()
    return out


def get_obj(klass, fieldname, obj):
    field_lookup = {
        fieldname: obj
    }
    return klass.objects.get_or_create(**field_lookup)[0]


def fetch(key, val_function, **kwargs):
    val = cache.get(key)
    if not val:
        val = val_function(**kwargs)
        cache.set(key, val)
    return val


def get_user_from_cache(key, obj, fieldname, classname):
    return fetch(key, get_obj, klass=classname, fieldname=fieldname, obj=obj)


def get_start_date():
    return delorean.Delorean(
        datetime=delorean.move_datetime_day(
            NOW().datetime,
            'last',
            TIME_SHIFT
        )).shift(ZUR_TZ).epoch()


def get_end_date():
    return delorean.Delorean(
        datetime=delorean.Delorean().midnight()).shift(ZUR_TZ).epoch()