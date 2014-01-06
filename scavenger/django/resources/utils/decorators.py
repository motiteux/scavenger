#!/bin/env python
# -*- coding: utf-8 -*-
#
# Created on 24/06/2013

"""Project level decorators

"""

__all__ = [
    'disable_for_loaddata'
]

import inspect
from functools import wraps
from time import time

from django.db.models.signals import post_init



def track_data(*fields):
    """
    Tracks property changes on a model instance.

    The changed list of properties is refreshed on model initialization
    and save.

    >>> @track_data('name')
    >>> class Post(models.Model):
    >>>     name = models.CharField(...)
    >>>
    >>>     @classmethod
    >>>     def post_save(cls, sender, instance, created, **kwargs):
    >>>         if instance.has_changed('name'):
    >>>             print "Hooray!"
    """

    UNSAVED = dict()

    def _store(self):
        "Updates a local copy of attributes values"
        if self.id:
            self.__data = dict((f, getattr(self, f)) for f in fields)
        else:
            self.__data = UNSAVED

    def inner(cls):
        # contains a local copy of the previous values of attributes
        cls.__data = {}

        def has_changed(self, field):
            "Returns ``True`` if ``field`` has changed since initialization."
            if self.__data is UNSAVED:
                return False
            return self.__data.get(field) != getattr(self, field)
        cls.has_changed = has_changed

        def old_value(self, field):
            "Returns the previous value of ``field``"
            return self.__data.get(field)
        cls.old_value = old_value

        def whats_changed(self):
            "Returns a list of changed attributes."
            changed = {}
            if self.__data is UNSAVED:
                return changed
            for k, v in self.__data.iteritems():
                if v != getattr(self, k):
                    changed[k] = v
            return changed
        cls.whats_changed = whats_changed

        # Ensure we are updating local attributes on model init
        def _post_init(sender, instance, **kwargs):
            _store(instance)
        post_init.connect(_post_init, sender=cls, weak=False)

        # Ensure we are updating local attributes on model save
        def save(self, *args, **kwargs):
            save._original(self, *args, **kwargs)
            _store(self)
        save._original = cls.save
        cls.save = save
        return cls
    return inner


def disable_for_loaddata(signal_handler):
    """
    See: https://code.djangoproject.com/ticket/8399
    Disables signal from firing if its caused because of loaddata
    """
    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        for fr in inspect.stack():
            if inspect.getmodulename(fr[1]) == 'loaddata':
                return
        signal_handler(*args, **kwargs)
    return wrapper


def timed(func):
    """Timer decorator

    :param func: object to decorate
    :param log_lvl: level for the log
    """
    @wraps(func)
    def wrapper(*args, **kwds):
        """Wrapper func"""
        start = time()
        result = func(*args, **kwds)
        elapsed = time() - start
        # print "%s took %d seconds to finish" % (func.__name__, elapsed)
        return result
    return wrapper