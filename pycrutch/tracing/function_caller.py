#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @author: Oren Tirosh
# src: http://code.activestate.com/recipes/578422-one-liner-to-show-the-caller-of-the-current-functi/

"""
This is a quick one-liner to produce the filename and line number of the caller of the current function.

This is useful for debugging and logging. It also nicely demonstrates the attribute access feature of the .format() method format string. If you wrap it in a function change the argument to _getframe() to 2. Add '{0.f_code.co_name}' to the format string to get the name of function containing the call site.
"""

'{0.f_code.co_filename}:{0.f_lineno}'.format(sys._getframe(1))
