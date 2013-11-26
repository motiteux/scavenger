# -*- coding: utf-8 -*-

"""Killing children pids using signals"""

__author__ = 'marco'

import os
import sys
import logging
import signal

logger = logging.getLogger('scavenger.multi.sigterm')


def sigterm_handler(signal, frame, pids):
    """Signal to propagate for ending simulations"""
    for pid in pids:
        logger.log_critical('Simulations ended {0}\n'.format(pid))
        try:
            os.kill(pid, 15)
        except OSError:
            logger.log_critical('Process {0} already stopped'.format(pid))
            continue
    sys.exit(0)


def sigint_handler(signal, frame, pids):
    """Signal to propagate for killing simulations"""
    for pid in pids:
        try:
            os.kill(pid, 9)
        except OSError:
            logger.log_critical('Process {0} already stopped'.format(pid))
            continue
    logger.log_critical('You pressed Ctrl+C!\n')
    sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)
signal.signal(signal.SIGTERM, sigterm_handler)