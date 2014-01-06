#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Created on 08/04/2013

"""Mixin classes for tests in UserProfile

"""

__all__ = [
    'BaseTestProfileMixin'
]

import logging

logger = logging.getLogger('userprofile.tests')

from django.conf import settings
from django.contrib.auth.models import Group, User

try:
    from mock import patch
    from fakeldap import MockLDAP
except ImportError:
    logger.debug("error import mock packages")
    IMPORT_MOCK = False
else:
    IMPORT_MOCK = True
    _mock_ldap = MockLDAP()


class TestUserProfileMixin(object):
    """Base class mixin for test cases in UserProfile."""

    fixtures = [
        'fixture_data.json',
        # 'test_ad.json',
    ]
    users = dict()
    groups = dict()

    def setUp(self):
        self.groups['Admin'] = Group.objects.get_or_create(
            name=settings.BOOK_ADMINS['my_admin'])[0]
        # Etc...

        self.users['myuser'] = self._initialize_test_user(
            'myuser',
            password='smith',
            groups=[self.groups['Admin']])
        # Etc...

        self.test_login_user = self._initialize_test_user(
            'test_client',
            password='toto',
            groups=[self.groups['Readers']],
            )

        if IMPORT_MOCK:
            # Patch where the ldap library is used:
            self.ldap_patcher = patch('userprofile.auth.ldap.initialize')
            self.mock_ldap = self.ldap_patcher.start()
            self.mock_ldap.return_value = _mock_ldap

    def tearDown(self):
        """Tear down unit tests"""
        for user in self.users.values():
            user.delete()
        for group in self.groups.values():
            group.delete()

        self.test_login_user.delete()

        if IMPORT_MOCK:
            _mock_ldap.reset()
            self.mock_ldap.stop()

    def _initialize_test_user(self, username, groups=None, password=None):
        """Create a UserProfile for test, without LDAP mapping.

        :param username: username to create a User with
        :param groups: list of groups to add this user to
        :param password: its password (if needed)

        :returns an instance of User
        """
        user, created = User.objects.get_or_create(
            username=username,
            first_name=username.capitalize(),
            last_name=username.upper(),
            email='%s@%s.com' % (username, "myemail")
        )
        if not created:
            return user

        if not password:
            user.set_unusable_password()
        else:
            user.set_password(password)

        user.is_staff = True
        user.save()

        if groups:
            for group in groups:
                group.user_set.add(user)

        profile = user.profile

        profile.job_title = "Test user"
        profile.telephone = "0999999999"
        profile.team = "Test Team"
        profile.city = "London"
        profile.team_leader = self._initialize_test_user(username="Superboss") \
            if user.username is not "Superboss" else None
        profile.language = "en-US"

        profile.save()

        return user
