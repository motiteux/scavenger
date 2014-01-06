#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Created on Jan 1st, 2014

"""Docstring"""

from functools import wraps
from time import time
# import logging


def timed(func, log_lvl=None):
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
        # logging.log("%s took %d seconds to finish" % (func.__name__, elapsed),
        #             log_lvl)
        return result
    return wrapper
