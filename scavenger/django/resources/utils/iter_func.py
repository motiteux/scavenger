#!/bin/env python
# -*- coding: utf-8 -*-
#
# Created on 26/06/2013

"""Module docstring

"""

__all__ = [
    'grouper',
]


from itertools import izip, chain, repeat


def grouper(n, iterable, padvalue=None):
    """For itertools recipes, we group an iterable by n and pad values to the
    rest, if any.

    :param n: Number of groups
    :param iterable: the iterable to cut in chunks
    :param padvalue: number of item per group
    :returns generator like izip
    """
    return izip(*[chain(iterable, repeat(padvalue, n-1))]*n)