# -*- coding: utf-8 -*-

__author__ = 'marco'


def list_formatter(iterable, name=None):
    """Formatting string to take care of English grammar for list."""
    if len(iterable) == 0:
        raise Exception('list {0} is empty.'.format(name), __name__)
    if len(iterable) == 1:
        return '{0}'

    err_fmt = ', '.join("{{{0}}}".format(iter_el) for
                                iter_el in range(len(iterable) - 1))
    err_fmt += ' and {{{0}}}'.format(len(iterable) - 1)

    return err_fmt