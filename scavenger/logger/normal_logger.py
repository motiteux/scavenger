# -*- coding: utf-8 -*-

__author__ = 'marco'

import sys
import os
from os.path import join
import logging

class SplitStreamHandler(logging.Handler):

    """Handler for logging to dispatch records on both console stderr and in
    other streams if message level is above or equal to Error.

    This handler is useful when one wants to also see error messages in Apache
    logs, but only marked as ERROR+ but not the less important ones, which will
    still be streamed to the other handlers.

    """

    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):
        """mostly copy-paste from logging.StreamHandler

        :param record: str, message to emit on streams
        """
        try:
            msg = self.format(record)
            if record.levelno < logging.WARNING:
                stream = sys.stdout
            else:
                stream = sys.stderr
            fs = "%s\n"

            try:
                if (isinstance(msg, unicode) and
                    getattr(stream, 'encoding', None)):
                    ufs = fs.decode(stream.encoding)
                    try:
                        stream.write(ufs % msg)
                    except UnicodeEncodeError:
                        stream.write((ufs % msg).encode(stream.encoding))
                else:
                    stream.write(fs % msg)
            except UnicodeError:
                stream.write(fs % msg.encode("UTF-8"))

            stream.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


def define_logger(logs_path, log_level='INFO'):
    """Create the dict of parameters for logging."""
    try:
        if not os.path.exists(logs_path):
            os.mkdir(logs_path)
    except OSError:
        # Need this to log into stderr for tracking problems.
        # On Apache, this will be redirect to the ErrorLog.
        print >>sys.stderr, 'Cannot create {0} folder'.format(logs_path)
        print >>sys.stderr, 'Exiting...'
        sys.exit(-1)

    logging_dict = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(levelname)s %(asctime)s %(name)s.%(module)s.'
                          '%(funcName)s:L%(lineno)d ProcessNo:%(process)d/'
                          'ThreadNo:%(thread)d "%(message)s"',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
            'normative': {
                'format': '%(levelname)s %(asctime)s %(module)s.'
                          '%(funcName)s:L%(lineno)d "%(message)s"',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
        },
        'handlers': {
            'null': {
                'level': 'DEBUG',
                'class': 'logging.NullHandler',
            },
            'default': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
                'stream': sys.stdout
            },
            'errors': {
                'level': 'WARNING',
                'class': 'prometheus.utils.string_helpers.SplitStreamHandler',
                'formatter': 'normative'
            },
            'default_file': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': join(logs_path, 'prometheus.log'),
                'maxBytes': 1024 * 1024 * 5,  # 5 MB
                'backupCount': 5,
                'formatter': 'standard',
            },
        },
        'loggers': {
            '': {
                'handlers': ['default'],
                'level': 'INFO',
                'propagate': True
            },
            'default': {
                'handlers': ['default_file', 'errors', 'console'],
                'level': log_level,
                'propagate': False,
            },
        }
    }

    if log_level == 'DEBUG':
        # make all loggers use the console.
        for logger in logging_dict['loggers']:
            logging_dict['loggers'][logger]['handlers'] = ['console']

    return logging_dict