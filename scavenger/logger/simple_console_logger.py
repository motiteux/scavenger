# -*- coding: utf-8 -*-

"""Logging class to print message on screen with colors.

class Logs(boolean) -- boolean to true sets the color printing

default_logger -- a non-color default logger
"""

from __future__ import print_function

__all__ = ['Logs', 'default_logger']


import colorama
import functools
import time

colorama.init(autoreset=True)

log_level = {
    'critical': ('BRIGHT', 'RED'),
    'warning': ('DIM', 'CYAN'),
    'normal': ('BRIGHT', 'BLUE'),
    'misc': ('DIM', 'GREEN')
}


def _log_color(*argsc):
    def wrap(func):
        @functools.wraps(func)
        def wrapped_f(*args):
            if len(argsc) == 0 or not args[0].color:
                arguments = '{0}'.format(args[1])
                return func(args[0], arguments)
            elif len(argsc) == 1 or (len(argsc) == 2 and len(args) == 2):
                arguments = getattr(colorama.Fore, log_level[argsc[0]][1]) + \
                        getattr(colorama.Style, log_level[argsc[0]][0]) + \
                        '{0}'.format(args[1])
                return func(args[0], arguments)
            elif len(argsc) == 2 and len(args) == 3:
                arguments = getattr(colorama.Fore, args[2]) + \
                        getattr(colorama.Style, log_level[argsc[0]][0]) + \
                        '{0}'.format(args[1])
                return func(args[0], arguments)
        return wrapped_f
    return wrap


class Logs(object):

    """Class for logging."""

    def __init__(self, color):
        """Initialization."""
        self.color = color
        self.msg = ''
        self.debug = False

    def set_debug(self, debug=True):
        """Set to debug mode (by default)."""
        self.debug = debug

    def modif_msg(self, msg):
        """Modify msg."""
        self.msg = '{0:s}'.format(msg)

    @_log_color('critical')
    def log_critical(self, msg=''):
        """Log method for printing critical message."""
        print(msg)

    @_log_color('warning')
    def log_warning(self, msg=''):
        """Log method for printing warning message."""
        print(msg)

    @_log_color('normal')
    def log_normal(self, msg=''):
        """Log method for printing normal message."""
        print(msg)

    @_log_color('misc', 'GREEN')
    def log_misc(self, msg=''):
        """Log method parameterizable with a specific color. Default is GREEN"""
        print(msg)

    @_log_color('misc', 'GREEN')
    def log_debug(self, msg=''):
        """Log method parameterizable with a specific color. Default is GREEN"""
        #TODO: Integration/Logger
        # Check the debug mode for the logs
        if self.debug:
            print('DEBUG [{0}]: {1}'.format(time.ctime(), msg))
        else:
            pass

    def update_color(self, color=False):
        """Update Log according to sys.argv options."""
        self.color = color

DEFAULT_LOGGER = Logs(False)
