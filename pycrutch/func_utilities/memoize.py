#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Created on 7/30/13

"""
From https://github.com/sdiehl/combine/blob/master/memoize.py
"""


def memoize(fn):
    memo = {}

    def wrapper(arg):
        if arg in memo:
            return memo[arg]
        else:
            result = fn(arg)
            memo[arg] = result
            return result
    return wrapper


if __name__ == '__main__':
    @memoize
    def fib(x):
        if x == 0:
            return 0
        elif x == 1:
            return 1
        else:
            return fib(x-1) + fib(x-2)

    print fib(29)

    def fib_slow(x):
        if x == 0:
            return 0
        elif x == 1:
            return 1
        else:
            return fib_slow(x-1) + fib_slow(x-2)

    print fib_slow(29)