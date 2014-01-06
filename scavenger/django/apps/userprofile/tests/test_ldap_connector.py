#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Created on 08/04/2013

"""This is the unittest to validate data imported from LDAP

"""

__all__ = [
    'TestUserDataValidation',
]

import logging

from django.conf import settings
from django.test import TestCase
from django.utils import unittest

import userprofile.auth.ldap_connector as ldap_connector
from userprofile.auth import LDAPUser
from ..utils import user_is_editor, user_is_owner, user_is_reader

from userprofile.tests.base_test_userprofile import TestUserProfileMixin


logging.disable(logging.CRITICAL)


class TestUserDataValidation(TestUserProfileMixin, TestCase):

    """TestCase class for LDAPUser class."""

    @unittest.skipUnless(settings.LDAP_TEST_USER
                         and settings.LDAP_TEST_PASSWORD,
                         'ActiveDirectory handshake tested only if personal '
                         'login are provided')
    def test_hierarchy(self):
        """Test if test user `reader` has a proper hierarchy
        """
        # self.assertTrue(self.client.login(username=settings.LDAP_TEST_USER,
        #                                   password=settings.LDAP_TEST_PASSWORD))

        self.assertTrue(ldap_connector.connect(settings.LDAP_TEST_USER,
                                               settings.LDAP_TEST_PASSWORD),
                        "Could not connect to LDAP")

        ad_lookup = LDAPUser(ldap_connector.LDAP_CONNECTION)
        ad_lookup.lookup_name = 'toto'

        user = ad_lookup.generate_user()

        self.assertIsNotNone(user, "user is a NoneType")

        self.assertTrue(user.username == 'toto')
        self.assertTrue(user.profile.city == 'London')
