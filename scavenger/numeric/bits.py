# -*- coding: utf-8 -*-

__author__ = 'marco'


def bit_at_p(int_number, place_bin):
    """find the bit at place p for number n"""
    # 2 ^ p, using bitshift, will have exactly one bit set, at place p
    two_p = 1 << place_bin

    # binary composition, will be one where *both* numbers have a 1 at that bit.
    # this can only happen at position p. will yield  two_p if N has a 1 at
    # bit p
    bin_comp = int_number & two_p

    return int(bin_comp > 0)
