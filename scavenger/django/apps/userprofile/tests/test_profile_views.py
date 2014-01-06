#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Created on 08/04/2013

"""Test for views in userprofile apps
"""

__all__ = [
    'TestUserProfileViews',
]


import logging

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from .base_test_userprofile import TestUserProfileMixin


logging.disable(logging.CRITICAL)


class TestUserProfileViews(TestUserProfileMixin, TestCase):

    """TestCase class for views."""

    def test_view_team_members(self):
        """Test if team member view is available"""
        c = Client()

        c.login(username=self.users['myuser'].username, password='smith')

        url = reverse('my-team', args=(self.users['myuser'].username,))
        response = c.get(url)

        self.assertEqual(response.status_code, 200)
