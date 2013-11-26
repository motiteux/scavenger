# -*- coding: utf-8 -*-

"""
Examples:

    @predicate
    def predicate_contraste(name, name_template='test'):
        return name == name_template

    @predicate
    def predicate_slow(name):
        return len(name) % 2 == 0

    @predicate
    def predicate_exists(name):
        return is_simulation(name)

    combined_predicates = ((predicate_contraste & predicate_slow) &
                           negate_predicate(
                               predicate_contraste & predicate_exists))

    filter_list = [cur_name for cur_name in
                   filter(combined_predicates, list_sim)]

"""

__author__ = 'marco'

import logging
import copy
from functools import update_wrapper
from functools import wraps

logger = logging.getLogger(__name__)


class NewPredicate(object):

    """Class to manage composition of predicates."""

    def __init__(self, predicate, name=None):
        """Init function.

        ------------
        Parameters:
            predicate: callable argument
                predicate must be a callable argument (function, lambda or
                method) and it must return a boolean when called.
            name: string
                If not defaulted, name must reflect the name of the predicate to
                use. In further methods, logs can use NewPredicate(predicate)
                names to reflect error messages.

        --------
        Remarks:
            Obviously, we only test if predicate is a callable.
        """
        if not hasattr(predicate, '__call__'):
            logger.log_warning(
                'Init function: {0} is not a predicate. Returning only '
                'Identity function (arguments passed to the predicate'.format(
                    predicate.__name__))
            self.pred = NewPredicate.identity
        self.pred = predicate
        if name is not None:
            self.pred.__name__ = name
        else:
            self.pred.__name__ = predicate.__name__

    @staticmethod
    def identity(*args):
        """Identity predicate."""
        if len(args) == 1:
            return args[0]
        return args

    def __call__(self, obj):
        """Keeps callable nature of predicates, so we can chain them."""
        return self.pred(obj)

    def copy_pred(self):
        """Provide a copy method (only shallow copy: predicate should not be
        a compound object)."""
        return copy.copy(self.pred)

    def __and__(self, predicate):
        """Method to overload & bitwise AND for predicates."""
        def pred_and(obj):
            """function used to perform AND operation on actual predicates."""
            if not hasattr(predicate, '__call__'):
                logger.log_warning(
                    'AND function: {0} is not a predicate. Returning only '
                    '{1}'.format(predicate.__name__, self.pred.__name__))
                return self.pred(obj)
            else:
                return self.pred(obj) and predicate(obj)
        return NewPredicate(pred_and, '{0} & {1}'.format(self.pred.__name__,
                                                         predicate.__name__))

    def __or__(self, predicate):
        """Method to overload | bitwise OR for predicates"""
        def pred_or(obj):
            """function used to perform AND operation on actual predicates."""
            if not hasattr(predicate, '__call__'):
                logger.log_warning(
                    'OR function: {0} is not a predicate. Returning only '
                    '{1}'.format(predicate.__name__, self.pred.__name__))
                return self.pred(obj)
            else:
                return self.pred(obj) or predicate(obj)
        return NewPredicate(pred_or, '{0} & {1}'.format(self.pred.__name__,
                                                        predicate.__name__))


def predicate(func):
    """Decorator that constructs a predicate (``NewPredicate``) instance from
    the given function."""
    result = NewPredicate(func)
    update_wrapper(result, func)
    return result


def negate_predicate(func):
    """Returns the negation of the predicate func."""
    @wraps(func)
    def wrapper(*args, **kwds):
        """Wrapper function."""
        return not func(*args, **kwds)
    wrapper.__name__ = 'negate_predicate({0})'.format(func.__name__)
    return wrapper
