#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Created on 27/02/2013

"""Settings for UserProfile"""

from django.conf import settings


# Defining global level LDAP options, may be overriden from settings.
DEFAULT_LDAP_SETTINGS = {
    'LDAP_SETTINGS': {
        'OPT_PROTOCOL_VERSION': 'VERSION3',
        'OPT_X_TLS_REQUIRE_CERT': 'OPT_X_TLS_NEVER',
        'OPT_X_TLS': 'OPT_X_TLS_DEMAND',
        'OPT_X_TLS_DEMAND': True,
        'OPT_REFERRALS': 0,
        'OPT_NETWORK_TIMEOUT': 10,
        'OPT_DEBUG_LEVEL': 0,
    },
    'TRACE_LEVEL': 0,
}

LDAP_CONF_SETTINGS = getattr(settings,
                             'LDAP_CONF_SETTINGS',
                             DEFAULT_LDAP_SETTINGS)

EXCLUDED_PATTERNS = getattr(settings, 'EXCLUDED_PATTERNS', [])
