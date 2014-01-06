#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Created on Jan 7, 2013

"""
This command populates (or modify) the (pre-existing) django user table from an
Active Directory using LDAP. This command must be supplied with an active AD 
user (ser_web_ldap?) in order to perform the queries.
"""

#TODO: Store as a tree instead, and start with roots...

__all__ = [
    'Command',
]

import re
import string
import logging
import ConfigParser
import traceback
from optparse import make_option, OptionParser
from pprint import pprint

from django.conf import settings
from django.core.cache import cache
from django.core.management.base import BaseCommand, CommandError

import userprofile.auth.ldap_connector as ldap_connector


logger = logging.getLogger('userprofile.management.ldap_sync')


# Regex pattern in username to exclude from the import
re_white_spaces = [r'|({0})'.format(char) for char in string.whitespace]

EXCL_REGEX = r'(^admin)|(^adm)|(^ADM)|(^ser_)|(^_default)|(^trn_)|' \
             r'(^cec)|(^tst_)|(^test_)|(Winterthur)|(ExchIMACTest)|' \
             r'(^[a-zA-Z]*\.)|(^ICE_){0}'

LIST_REVOKED = re.compile(EXCL_REGEX.format(''.join(re_white_spaces)))


class Command(BaseCommand):
    help = "find information for user from LDAP."
    args = 'user_to_check --username=USER --passwd=PASSWORD| ' \
           '--file_options=file'

    option_list = BaseCommand.option_list + (
        make_option('--username',
                    type='str',
                    dest='username',
                    help='AD username'),
        make_option('--passwd',
                    type='str',
                    dest='passwd',
                    help='AD password'),
        make_option('--file_options',
                    type='str',
                    dest='file_opt',
                    help='Options stored in a config file',
                    metavar="FILE"),
    )

    def handle(self, *args, **options):
        if options['username'] and options['passwd']:
            pass
        elif not options['username'] and not options['passwd'] and \
                options['file_opt']:
            config = ConfigParser.ConfigParser()
            file_options = options.get('file_opt', None)
            if file_options is not None:
                config.read(file_options)

                parser = OptionParser()
                parser.add_option("--username",
                                  dest="username",
                                  help="AD username",
                                  default=config.get("AD identification",
                                                     "username"))
                parser.add_option("--passwd",
                                  dest="passwd",
                                  help="AD password",
                                  default=config.get("AD identification",
                                                     "password"))
                opts, _ = parser.parse_args()

                options = vars(opts)
        elif not options['username'] and not options['passwd'] and \
                not options['file_opt']:
            try:
                options['username'] = settings.LDAP_QUERY_USER or None
                options['passwd'] = settings.LDAP_QUERY_PASSWORD or None
            except AttributeError:
                raise CommandError("No credentials provided")
            finally:
                if not options['username'] or not options['passwd']:
                    raise CommandError("No credentials provided")

        if not args:
            raise CommandError("No username provided")

        usernames = args

        with ldap_connector.LDAPContextManager(options['username'],
                                               options['passwd'],
                                               paged=True) as ldap_conn:
            logger.info("Handshake with LDAP server {0:s} done".format(
                ldap_conn.ldap_url))
            try:
                # Send search request
                all_active_users = ldap_conn.ldap_lookup()

                # Clearing the cache to avoid key collision
                cache.clear()

                # Future connections will not be paged.
                #TODO: Need some optimization here
                ldap_conn.paged = False

                for username in usernames:
                    try:
                        user = next((ldap_user for ldap_user in
                                     all_active_users if ldap_user[0] and
                                     ldap_user[1].get(
                                         'sAMAccountName')[0] == username))
                        pprint(user)
                    except StopIteration:
                        logger.warning("User {0} could not be found in "
                                       "LDAP".format(username))
                        continue

            except Exception as err:
                # This exception could be re-raised for login views to catch and
                # deal with specifically
                logger.error(err.message)
                raise
            except Exception as exx_cp:
                tb = traceback.format_exc()
                logger.error(tb)
                raise exx_cp
