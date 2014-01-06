#!/bin/env python
# -*- coding: utf-8 -*-
#
# Created on 06/01/2014

"""Multi proc/thread helpers"""

__all__ = [
    'get_nb_workers',
]

import logging
import psutil


logger = logging.getLogger('scavenger.compute')


def get_nb_workers(force_max=False):
    """Retrieve the number of available workers. Leave at least one proc out
    for free (if not force_max).

    :param force_max: Boolean to force the use of the maximum number of
        available workers
    """
    if force_max:
        NB_PROC = psutil.NUM_CPUS
    else:
        if psutil.NUM_CPUS % 2 == 0:
            NB_PROC = psutil.NUM_CPUS - 2
        else:
            NB_PROC = psutil.NUM_CPUS - 1

        if NB_PROC == 0:
            NB_PROC = 1

    logger.info("Using {0} workers".format(NB_PROC))

    return NB_PROC
