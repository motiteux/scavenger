#!/usr/bin/env python
# -*- coding: utf-8 -*-


# @author: Eli Bendersky
# src: http://eli.thegreenplace.net/2012/08/22/easy-tracing-of-nested-function-calls-in-python/ 

"""
Sometimes, when executing algorithms with complex function call sequences, and
especially ones that require recursion, it’s useful to see what calls actually
occurred during execution, their arguments and return values, and so on.

And here’s how we can use it:

    @TraceCalls()
    def iseven(n):
        return True if n == 0 else isodd(n - 1)

    @TraceCalls()
    def isodd(n):
        return False if n == 0 else iseven(n - 1)

    print(iseven(7))

Output:

    iseven(7)
      isodd(6)
        iseven(5)
          isodd(4)
            iseven(3)
              isodd(2)
                iseven(1)
                  isodd(0)
    False

The indentation level is shared between different functions – this is a key
feature of the tracer. Note that the tracer is a class; while a function can
also serve as a decorator, I find a class easier to reason about. Moreover,
this tracer has some useful parameters to tweak and a decorator with arguments
is much simpler to express with a class. Here are the parameters:

    stream: the stream to print tracing output to. By default it’s printed to
    sys.stdout.
    indent_step: by how many space chars to grow the indentation for each
        nested call.
    show_ret: when True, shows the return value of each call.

What follows is an example that demonstrates a less linear call sequence and
also the usage of some of the parameters:

    @TraceCalls(indent_step=4 show_ret=True)
    def flatten(lst):
        if isinstance(lst, list):
            return sum((flatten(item) for item in lst), [])
        else:
            return [lst]

    list(flatten([1, 2, [3, [4, 5], 6, [7, [9], 12]], 4, [6, 9]]))

Output:

    flatten([1, 2, [3, [4, 5], 6, [7, [9], 12]], 4, [6, 9]])
        flatten(1)
        --> [1]
        flatten(2)
        --> [2]
        flatten([3, [4, 5], 6, [7, [9], 12]])
            flatten(3)
            --> [3]
            flatten([4, 5])
                flatten(4)
                --> [4]
                flatten(5)
                --> [5]
            --> [4, 5]
            flatten(6)
            --> [6]
            flatten([7, [9], 12])
                flatten(7)
                --> [7]
                flatten([9])
                    flatten(9)
                    --> [9]
                --> [9]
                flatten(12)
                --> [12]
            --> [7, 9, 12]
        --> [3, 4, 5, 6, 7, 9, 12]
        flatten(4)
        --> [4]
        flatten([6, 9])
            flatten(6)
            --> [6]
            flatten(9)
            --> [9]
        --> [6, 9]
    --> [1, 2, 3, 4, 5, 6, 7, 9, 12, 4, 6, 9]

"""

__authors__ = [  # alphabetical order by last name, please
               '"Marc-Olivier Titeux" <marc-olivier.titeux@ifpen.fr>'
               ]

__all__ = ['TraceCalls']


import sys
from functools import wraps


class TraceCalls(object):
    """ Use as a decorator on functions that should be traced. Several
        functions can be decorated - they will all be indented according
        to their call depth.
    """
    def __init__(self, stream=sys.stdout, indent_step=2, show_ret=False):
        self.stream = stream
        self.indent_step = indent_step
        self.show_ret = show_ret

        # This is a class attribute since we want to share the indentation
        # level between different traced functions, in case they call
        # each other.
        TraceCalls.cur_indent = 0

    def __call__(self, fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            indent = ' ' * TraceCalls.cur_indent
            argstr = ', '.join(
                [repr(a) for a in args] +
                ["%s=%s" % (a, repr(b)) for a, b in kwargs.items()])
            self.stream.write('%s%s(%s)\n' % (indent, fn.__name__, argstr))

            TraceCalls.cur_indent += self.indent_step
            ret = fn(*args, **kwargs)
            TraceCalls.cur_indent -= self.indent_step

            if self.show_ret:
                self.stream.write('%s--> %s\n' % (indent, ret))
            return ret
        return wrapper
