#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Created on Oct 29, 2012

"""
Docstring
"""

__all__ = [
    'LoggedInMixin',
    'FilterMixin',
    'CheckContextMixin',
    'SortMixin',
    'AjaxableResponseMixin',
    'FormListView',
]

import logging
import json

from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.http import HttpResponse


logger = logging.getLogger('junglebook')


class FilterMixin(object):

    """Inject specific filters in queryset."""

    allowed_filters = {}
    allowed_excludes = {}

    def dispatch(self, request, *args, **kwargs):
        """Dispatch injection to use mixin in CBV"""
        return super(FilterMixin, self).dispatch(
            request, *args, **kwargs)

    def get_queryset_filters(self):
        """Define the filters"""
        filters = {}
        for item in self.allowed_filters:
            if self.allowed_filters[item]:
                filters[item] = self.allowed_filters[item]
        return filters

    def get_queryset_excludes(self):
        """Define the excludes"""
        excludes = {}
        for item in self.allowed_excludes:
            # if self.allowed_excludes[item]:
            excludes[item] = self.allowed_excludes[item]
        return excludes

    def get_queryset(self):
        """Combine filter/exclude"""
        qs = super(FilterMixin, self).get_queryset().filter(**self.get_queryset_filters())
        # Excludes can be mutually exclusive...
        for item in self.allowed_excludes:
            qs = qs.exclude(**{item: self.allowed_excludes[item]})

        return qs


class SortMixin(object):

    """Inject specific sorting in queryset."""

    instance_sorters = []

    def dispatch(self, request, *args, **kwargs):
        """Dispatch injection to use mixin in CBV"""
        return super(SortMixin, self).dispatch(
            request, *args, **kwargs)

    def get_queryset_sorters(self):
        """Define the filters"""
        sorters = []
        map_order = {
            'ascending': '',
            'descending': '-',
        }
        for item in self.instance_sorters:
            sorters.append(map_order[item[1]] + item[0])
        return sorters

    def get_queryset(self):
        return super(SortMixin, self).get_queryset()\
            .order_by(*self.get_queryset_sorters())


class AjaxableResponseMixin(object):

    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """

    def dispatch(self, request, *args, **kwargs):
        """Dispatch injection to use mixin in CBV"""
        return super(AjaxableResponseMixin, self).dispatch(
            request, *args, **kwargs)

    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    def form_invalid(self, form):
        if self.request.is_ajax():
            return self.render_to_json_response(form.errors, status=400)
        else:
            return super(AjaxableResponseMixin, self).form_invalid(form)

    def form_valid(self, form):
        if self.request.is_ajax():
            data = {
                'pk': form.instance.pk,
            }
            return self.render_to_json_response(data)
        else:
            return super(AjaxableResponseMixin, self).form_valid(form)


def filter_action(request):
    """Redirect view used for the forms action

    :param request: current request
    """
    return HttpResponseRedirect('')
