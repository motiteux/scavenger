#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Created on Nov 15, 2012

"""
Module doc
"""

__all__ = [
    'list_formatter',
]

import sys
import logging


def list_formatter(iterable, name=None):
    """Formatting string to take care of English grammar for list."""
    if len(iterable) == 0:
        return None
    if len(iterable) == 1:
        return iterable[0]

    list_fmt = ', '.join(map(str, iterable[:-1]))
    list_fmt += ' and {0}'.format(iterable[-1])

    return list_fmt


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
