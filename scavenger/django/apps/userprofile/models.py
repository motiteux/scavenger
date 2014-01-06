#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Created on Oct 5, 2012

"""
Models for user profiles
"""

__all__ = [
    'UserProfile',
]

import datetime

from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from tastypie.models import create_api_key

from ..resources.utils.utils import get_user_from_cache

from ..resources.utils.cache import fix_key

from .signals import create_profile


class UserProfile(models.Model):

    """Profile that extends User, in BooK."""

    user = models.OneToOneField(User,
                                primary_key=True,
                                related_name="user")

    # Some last name are too long for auth.User, so we duplicate them here
    last_name_prof = models.CharField(
        max_length=75,
        verbose_name=_('Last name'),
        null=False,
        blank=True,
        default='',
    )

    # Identification and contact
    telephone = models.CharField(
        max_length=30,
        verbose_name=_('Mobile number'),
        default='',
        blank=True,
        validators=[
            RegexValidator(
                regex='^\+{0,1}(?=(?:\D*\d){6,15}$)[\d .()-]+$'
            )
        ]
    )

    city = models.CharField(max_length=64,
                            verbose_name=_('City'),
                            default='',
                            blank=True
                            )

    team_leader = models.ForeignKey(
        User,
        verbose_name=_(u"Team leader"),
        related_name="%(app_label)s_%(class)s_team_leader",
        null=True,
        blank=True)
    team_leader_status = models.BooleanField(_("Am I a team-leader"),
                                             default=False,
                                             blank=False,
                                             )
    team = models.CharField(max_length=64,
                            verbose_name=_(u"Team"),
                            default='',
                            blank=True)
    department = models.CharField(max_length=64,
                                  verbose_name=_(u"Department"),
                                  default='',
                                  blank=True)
    job_title = models.CharField(max_length=64,
                                 verbose_name=_(u"Job title"),
                                 default='',
                                 blank=True)
    role = models.TextField(max_length=750,
                            verbose_name=_(u"Role"),
                            null=True,
                            blank=True)
    skills = models.TextField(max_length=750,
                              verbose_name=_(u"Skills"),
                              null=True,
                              blank=True)

    class Meta:
        verbose_name = 'User profile'
        verbose_name_plural = 'User profiles'

    def key_from_instance(self):
        """Key used for the cache"""
        name = ' '.join([unicode(self.user.last_name),
                         unicode(self.user.first_name)])
        return fix_key(name)

    def __unicode__(self):
        return unicode(self.user.get_full_name().strip() or self.user.username)

    def __str__(self):
        return self.user.username

User.profile = property(lambda u: get_user_from_cache("user_get_or_create_profile_{0}".format(u.username), u, 'user', UserProfile))

post_save.connect(create_profile, sender=User,
                  dispatch_uid="userprofile-creation-profile")

#FIX: from http://stackoverflow.com/a/13171921
try:
    post_save.connect(create_api_key, sender=User,
                      dispatch_uid="userprofile-creation-apikey")
except Exception, e:
    pass
