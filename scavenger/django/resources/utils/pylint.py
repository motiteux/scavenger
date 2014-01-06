#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Created on Dec 20, 2012

'''
Pylint wrapper for Django
'''


from django.core.management.base import BaseCommand
from django.conf import settings

from pylint import lint


class Command(BaseCommand):
    def handle(self, *args, **options):
        if getattr(settings, 'DEBUG', False):
            rcfile = getattr(settings, 'RCFILE', '')
            lint.Run(list(args + ("--rcfile={0}".format(rcfile),)), exit=False)
