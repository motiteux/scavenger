#!/bin/env python
# -*- coding: utf-8 -*-
#
# Created on 27/06/2013

"""Multi proc/thread helpers"""

__all__ = [
    'get_nb_workers',
    'reconnect_db',
    'reset_database_connection',
]

import logging
import psutil


logger = logging.getLogger('default.utils.multi')


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


def reconnect_db():
    """Keeping DB connection alive across processes"""
    from django.db import connections

    reset_database_connection()

    cur_db = connections['default']
    if cur_db.connection is not None and hasattr(cur_db.connection, 'ping'):
        cur_db.connection.ping()
    else:
        cur_db.cursor()


def reset_database_connection():
    """Close current db connection"""
    from django import db
    from django.db import connections

    conn = connections['default']
    cursor = conn.cursor()
    if cursor and conn:
        cursor.close()
        # conn.close()
    db.close_connection()

