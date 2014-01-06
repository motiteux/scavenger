#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Created on Jan 6, 2014

"""
Admin for Models.
Snippet for list_filter_collapse in admin.
"""

from django.contrib import admin

import myapp.models


class MyModelAdmin(admin.ModelAdmin):
    max_num = 1
    list_display = ('__unicode__',
                    'attribute',
                    )
    list_filter = ('attribute')
    search_fields = ('attribute__first_attr',
                     'attribute__last_attr',
                     '__unicode__')

    class Media:
        js = ['js/extras/list_filter_collapse.js']

admin.site.register(myapp.models.MyModel, MyModelAdmin)
