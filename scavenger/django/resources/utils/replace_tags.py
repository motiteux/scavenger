#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Created on 8/19/13

"""This will perform a regular expression search/replace on a string in your
template.
{% load replace %} {{ mystring|replace:"/l(u+)pin/m\1gen" }}
If:
mystring = 'lupin, luuuuuupin, and luuuuuuuuuuuuupin are lè pwn'
then it will return:
mugen, muuuuuugen, and muuuuuuuuuuuuugen are lè pwn

The argument is in the following format:
[delim char]regexp search[delim char]regexp replace

"""

import re

from django import template
register = template.Library()


@register.filter
def replace(string, args):
    """Replace matched string with args"""
    search = args.split(args[0])[1]
    replace_val = args.split(args[0])[2]

    return re.sub( search, replace_val, string )