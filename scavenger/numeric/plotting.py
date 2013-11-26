# -*- coding: utf-8 -*-

__author__ = 'marco'


import numpy as np

from .numbers import get_exponent


def get_minmaxxyrange(time_vals, *args):
    """Compute min/max range for a list of lists of values.

    -----------
    Parameters:
        time_vals : list of floats
            list of time steps
        args: lists of floats
            lists of flux values

    --------
    Returns:
        A range [time_min, time_max], [ymin, ymax] such as ymin is the minimum
        of all ymin of the iterables and ymax is the maximum of all ymax of the
        iterables.

    """
    range_valminmax = {'min': [], 'max': []}
    range_time = list()
    range_time.append([np.min(time_vals), np.max(time_vals)])
    for iter_list in args:
        m_iter = np.array([iter_flux for iter_flux in iter_list
                              if iter_flux != 0.])
        if len(m_iter) == 0:
            raise Exception('Arctem simulation did not converge.\n'
                            'Please check traceback for name.')
        range_valminmax['min'].append(m_iter.min())
        range_valminmax['max'].append(m_iter.max())

    # Time min is offset by 1: no velocity at first step
    range_timeminmax = [np.min(range_time), np.max(range_time)]
    val_min = np.min(range_valminmax['min'])
    val_max = np.max(range_valminmax['max'])

    return [range_timeminmax[0],
            range_timeminmax[1],
            np.sign(val_min) * pow(10, get_exponent(val_min)[1] - 1),
            np.sign(val_max) * pow(10, get_exponent(val_max)[1] + 1)
            ]


def get_minmaxxyranges(list_vals):
    """Compute min/max range for a list of lists of values.

    -----------
    Parameters:
        list_vals : iterable of iterables of float elements

    --------
    Returns:
        A range [ymin, ymax] such as ymin is the minimum of all ymin of the
        iterables and ymax is the maximum of all ymax of the iterables.

    """
    range_valminmax = []
    range_time = []
    for iter_lists in list_vals:
        val_range = get_minmaxxyrange(*iter_lists)
        range_time.append([val_range[0], val_range[1]])
        range_valminmax.append(val_range[2])
        range_valminmax.append(val_range[3])

    range_timeminmax = [np.min(range_time), np.max(range_time)]
    val_min = np.min(range_valminmax)
    val_max = np.max(range_valminmax)

    return [range_timeminmax[0],
            range_timeminmax[1],
            val_min,
            val_max
            ]