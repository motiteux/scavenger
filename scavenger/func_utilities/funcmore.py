# -*- coding: utf-8 -*-

__author__ = 'marco'

from itertools import izip_longest


def grouper(iterable, n_item, fillvalue=None):
    """group name per batch of n elements."""
    return izip_longest(*[iter(iterable)] * n_item, fillvalue=fillvalue)


def izipmerge(iterable_a, iterable_b):
    """Creates an iterator of a zip(a, b) then filled with None if one of them
    is smaller than the other."""
    for iter_a, iter_b in izip_longest(iterable_a, iterable_b, fillvalue=None):
        yield iter_a
        yield iter_b


def filtertrue(predicate, iterable):
    """Return an iterator composed of elements x that satisfy predicate(x).

    Iterator version of filter method.

    --------
    Example:
    filtertrue(lambda x: x%2, range(10)) --> 0 2 4 6 8
    """
    if predicate is None:
        predicate = bool
    for iter_x in iterable:
        if predicate(iter_x):
            yield iter_x


def pairs_range(limit1, limit2):
    """Produce all pairs in (0..`limit1`-1, 0..`limit2`-1)"""
    for iter_1 in range(limit1):
        for iter_2 in range(limit2):
            yield iter_1, iter_2