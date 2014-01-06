#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Created on Oct 16, 2012

"""
Module doc
"""

from django.contrib import admin
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.utils.html import escape
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.encoding import smart_unicode
from django.utils.translation import gettext_lazy as _


class LogEntryAdmin(admin.ModelAdmin):

    date_hierarchy = 'action_time'

    readonly_fields = LogEntry._meta.get_all_field_names()

    list_filter = [
        # 'user',
        'content_type',
        # 'get_action_flag'
    ]

    search_fields = [
        'object_repr',
        'change_message'
    ]


    list_display = [
        'action_time',
        'user',
        'content_type',
        'object_link',
        # 'get_action_flag',
        # 'get_change_message',
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser and request.method != 'POST'

    def has_delete_permission(self, request, obj=None):
        return False

    def get_change_message(self, obj):
        return smart_unicode(obj.change_message)
    get_change_message.allow_tags = True
    get_change_message.admin_order_field = 'change message'
    get_change_message.short_description = "Change message"

    def get_action_flag(self, obj):
        action = _("No action")
        if obj.action_flag == ADDITION:
            action = _("Addition")
        if obj.action_flag == CHANGE:
            action = _("Modification")
        if obj.action_flag == DELETION:
            action = _("Deletion")
        return action
    get_action_flag.allow_tags = True
    get_action_flag.admin_order_field = 'action_flag'
    get_action_flag.short_description = "Action type"

    def object_link(self, obj):
        if obj.action_flag == DELETION:
            link = smart_unicode(escape(obj.object_repr))
        else:
            ct = obj.content_type
            link = mark_safe(u'<a href="%s">%s</a>' % (
                reverse('admin:%s_%s_change' % (ct.app_label, ct.model),
                        args=[obj.object_id]),
                obj.object_repr))
        return link
        # if obj.action_flag == DELETION:
        #     link = smart_unicode(escape(obj.object_repr))
        # else:
        #     ct = obj.content_type
        #     link = mark_safe(u'<a href="{0}">{1}</a>'.format(
        #             reverse('admin:%s_%s_change' % (ct.app_label, ct.model),
        #                     args=[obj.object_id]),
        #             obj.object_repr))
        # return link
    object_link.allow_tags = True
    object_link.admin_order_field = 'object_repr'
    object_link.short_description = u'object'


admin.site.register(LogEntry, LogEntryAdmin)