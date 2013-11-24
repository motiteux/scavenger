__author__ = 'marco'

import sys
from contextlib import contextmanager



@contextmanager
def manage_exit(log):
    """Context manager to use in prometheus.py. Deals with the proper series of
    Exceptions."""
    try:
        yield
    except (KeyboardInterrupt, SystemExit):
        raise
    #except PromNotImplementedError as err:
    #    log.critical('Feature {0} not implemented'.format(err.name_feature))
    #    log.critical('Please, contact {0}.\n\tExiting'.format(__authors__[0]))
    #    sys.exit(-1)
    #except PromError as err:
    #    log.critical(err.message + '\n\tExiting.', exc_info=True)
    #    sys.exit(-1)
    #except PromNotManaged as err:
    #    err.report_issue(log, plogging)
