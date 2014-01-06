#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Created on Nov 1, 2012

"""
This is the unittest for LDAP connection, high level test.
This is shaped to match my profile as LDAP connection involves personal
information
and requires to provide a personal.py in settings module that contains NTLM
username and password. And thus, it SHOULD not be part of SVN but if it is
missing
from the current code base, the tests will be skipped.

"""

__all__ = [
    'TestActiveDirectoryBackend',
]


import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import unittest
from django.utils.encoding import smart_unicode

from ..auth import LDAPUser
import userprofile.auth.ldap_connector as ldap_connector

from .base_test_UserProfile import TestUserProfileMixin


logging.disable(logging.CRITICAL)


class TestActiveDirectoryBackend(TestUserProfileMixin, TestCase):

    """TestCase class for ActiveDirectoryBackend class.

    Will also test User/profile creation (auth/auth_backend.py file).

    """

    @unittest.skipUnless(settings.LDAP_TEST_USER
                         and settings.LDAP_TEST_PASSWORD,
                         'ActiveDirectory handshake tested only if personal '
                         'login are provided')
    def test_handshake_ldapconnection(self):
        """Check connectivity with LDAP.
        This test runs only if a personal.py is provided in settings package
        containing NTLM login. This file SHOULD not be part of VCS.

        """
        self.assertTrue(self.client.login(
            username=settings.LDAP_TEST_USER,
            password=settings.LDAP_TEST_PASSWORD))

        # Change your username to match provided AD_USER in personal settings
        self.assertTrue(User.objects.filter(
            username=settings.LDAP_TEST_USER).count() == 1)

    @unittest.skipUnless(
        settings.LDAP_TEST_USER and settings.LDAP_TEST_PASSWORD,
        'ActiveDirectory sync tested only if personal login are provided')
    def test_adsync(self):
        """Check grasped information from Active Directory.
        This test runs only if a personal.py is provided in settings package
        containing NTLM login. personal.py SHOULD not be part of VCS.

        """
        # self.assertTrue(self.client.login(
        #     username=settings.LDAP_TEST_USER,
        #     password=settings.LDAP_TEST_PASSWORD))
        self.assertTrue(ldap_connector.connect(settings.LDAP_TEST_USER,
                                               settings.LDAP_TEST_PASSWORD))

        ad_lookup = LDAPUser(ldap_connector.LDAP_CONNECTION)
        ad_lookup.lookup_name = settings.LDAP_TEST_USER

        test_user = ad_lookup.generate_user()
        test_profile = test_user.profile

        self.assertTrue(test_user.is_superuser)
        self.assertTrue(test_user.is_staff)
        self.assertTrue('My Name' in smart_unicode(test_profile))
        self.assertTrue(self.groups.get('Admin') in test_user.groups.all())
        self.assertTrue(test_profile.telephone == '')
        self.assertTrue(test_profile.city == 'London')
        # self.assertTrue(test_profile.language == 'en-US')
        self.assertTrue(test_profile.team == 'My Team')
        self.assertTrue(test_profile.team_leader.username == 'myboss')
        self.assertTrue(test_profile.job_title == 'dev')

#    def test_profilecreation(self):
#        # Should test boolean member variables
#        pass
#    
#    def test_checkgroup(self):
#        pass
#    
#    def test_incompleteinfo(self):
#        pass
#    
#    def test_ldapsync(self):
#        pass
#
#    def test_disconnect(self):
#        pass