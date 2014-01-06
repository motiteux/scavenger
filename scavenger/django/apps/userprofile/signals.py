#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Created on Oct 26, 2012

"""
Hook into create/get profile from User
"""

from django.core.cache import cache
import django.dispatch

from ..resources.utils.decorators import disable_for_loaddata



@disable_for_loaddata
def create_profile(sender, instance, created, **kwargs):
    """Create the UserProfile when a new User is saved.

    :param sender: The model class.
    :param instance: The actual instance being saved.
    :param created: flag set at the creation of an instance, passed by Django

    """
    if created:
        profile, new = sender.objects.get_or_create(user=instance)
