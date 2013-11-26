# -*- coding: utf-8 -*-

__author__ = 'marco'

import numpy as np


def find_nearest(array, value):
    """Find nearest value to array."""
    return (np.abs(np.array(array) - value)).argmin()