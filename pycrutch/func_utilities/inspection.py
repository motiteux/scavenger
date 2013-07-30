#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Created on 4/30/13

"""Func to extract values and type of a function.
#TODO: Need be set as a decorator. Kept it here for bookkeeping.

"""

import inspect


def inspect_args(*args):
    """Analyze arguments of function and print them using inspect


    """
    frame = inspect.currentframe()
    args, _, _, values = inspect.getargvalues(frame)

    print 'function name "%s"' % inspect.getframeinfo(frame)[2]
    for i in args:
        print "    %s = %s" % (i, values[i])


