#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Created on Jan 1st, 2014

"""Docstring"""

import logging
import concurrent.futures

from .multi import get_nb_workers
from tracing.decorators_profiling import timed


logger = logging.getLogger('scavenger.compute')


@timed
def _dummy_func(*args, **kwargs):
    """Dummy function

    :param page: `CMS.models.Page` to check its categories
    """
    status = False
    err = False
    try:
        print "toto"

    except Exception as exx_cp:
        template = "An exception of type {0} occured. Arguments:\n{1!r}"
        message = template.format(type(exx_cp).__name__, exx_cp.args)
        logger.error(message)
        err = True

    return status, err


def dummy_func(max_proc=False):
    """Dummy function multi

    :param max_proc: Boolean, use all avail workers
    """
    # Encompass all pages actually
    all_objects = []
    
    processed_obj = []
    failed_obj = []
    nb_proc = get_nb_workers(max_proc)

    with concurrent.futures.ProcessPoolExecutor(max_workers=nb_proc) \
            as executor:
        future_to_objs = {executor.submit(
            _dummy_func, page):
            page for page in all_objects.iterator()}
        for future in concurrent.futures.as_completed(future_to_objs):
            obj = future_to_objs[future]
            try:
                status, err = future.result()
            except Exception as exx_cp:
                logger.error("There was an error in retrieving results for obj"
                             " {0}".format(obj))
                logger.error(exx_cp)
            else:
                if status:
                    processed_obj.append(obj)
                if err:
                    failed_obj.append(obj)

    return processed_obj, failed_obj, all_objects.count()

