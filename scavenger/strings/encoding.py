# -*- coding: utf-8 -*-

__author__ = 'marco'

from chardet import detect


def get_encoding(byte_string):
    """Detect encoding of input byte string"""
    return detect(byte_string)['encoding']

