# -*- coding: utf-8 -*-

__author__ = 'marco'


def multiple_ten(number, radix_exponent=10, order='ceil'):
    """Compute a the closest multiple of radix_exponent for number (which could
    be a float)."""
    remainder = number % radix_exponent
    if remainder:
        threshold = radix_exponent / 2
        if order == 'ceil':
            if remainder < threshold:
                return number - remainder
            elif remainder > threshold:
                return number + (radix_exponent - remainder)
        elif order == 'round':
            return number - remainder
        else:
            return 'nan'
    else:
        return number


def get_exponent(f_number):
    """Returns the exponent part of the scientific notation of f_number as an
    int.

    """
    parts = ("%e" % f_number).split('e')
    return float(parts[0]), int(parts[1])
