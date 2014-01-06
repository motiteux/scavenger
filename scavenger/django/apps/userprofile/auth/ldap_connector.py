#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Created on 08/04/2013

"""All LDAP interaction and utilities

Warning: There is a strong assumption for LDAP Queries that ldap usernames do
not contain whitespace. This was used to discriminate between username lookup
vs. full name lookup.
"""

__all__ = [
    'LDAP_URL',
    'LDAPContextManager',
    'adaccount_validator',
]

import sys
import types
import string
import logging
import ldap
import ldap.sasl
from ldap.controls import SimplePagedResultsControl

from django.conf import settings

from ..resources.utils.utils import get_exc_str
from .. import settings as userprofile_settings


class ConnectionError(Exception):
    pass

logger = logging.getLogger('userprofile.auth.connector')


LDAP_CONF_SETTINGS = userprofile_settings.LDAP_CONF_SETTINGS

# LDAP Query construct to search for valid users
SEARCH_FLT = r'(&(objectCategory=person)(objectClass=user)(|(' \
             r'userAccountControl:1.2.840.113556.1.4.803:=32)(' \
             r'!(userAccountControl:1.2.840.113556.1.4.803:=2))){0})'

# Paging size for the LDAP query
PAGE_SIZE = 100

# Helper string to ldap address.
LDAP_URL = "ldap://{0:s}:{1:s}".format(settings.AD_DNS_NAME,
                                       settings.AD_LDAP_PORT)


def _apply_ldap_options(ldap_conn, options_dict):
    """Change LDAP settings with [DEFAULT_]LDAP_SETTINGS dict

    :param ldap_conn: LDAPObject to apply the dict to
    :param options_dict: dict to update properties of LDAPObject. If value is a
        string, the ldap [key as in dict] option is an attribute from ldap
        object. Otherwise, the value can be applied directly.
    """
    for opt, value in options_dict.iteritems():
        if isinstance(value, str):
            ldap_conn.set_option(
                getattr(ldap, opt), getattr(ldap, value))
        else:
            ldap_conn.set_option(
                getattr(ldap, opt), value)


def _paged_search_ext_s(self, base, scope, search_flt,
                        filterstr='(objectClass=*)', attrlist=None, attrsonly=0,
                        serverctrls=None, clientctrls=None, timeout=-1,
                        sizelimit=0):
    """Behaves exactly like LDAPObject.search_ext_s() but internally uses
    the simple paged results control to retrieve search results in chunks.

    :param self:
    :param base:
    :param scope:
    :param search_flt:
    :param filterstr:
    :param attrlist:
    :param attrsonly:
    :param serverctrls:
    :param clientctrls:
    :param timeout:
    :param sizelimit:
    :type clientctrls: object
    """
    req_ctrl = SimplePagedResultsControl(True,
                                         size=PAGE_SIZE,
                                         cookie='')

    # Send first search request
    msgid = self.search_ext(
        settings.AD_SEARCH_DN,
        ldap.SCOPE_SUBTREE,
        # SEARCH_FLT,
        search_flt,
        attrlist=settings.AD_SEARCH_FIELDS.keys(),
        serverctrls=(serverctrls or []) + [req_ctrl]
    )

    result_pages = 0
    all_results = []

    while True:
        # Dependency injected from LDAPObject
        rtype, rdata, rmsgid, rctrls = self.result3(msgid)
        all_results.extend(rdata)
        result_pages += 1
        # Extract the simple paged results response control
        pctrls = [
            ctrl_t
            for ctrl_t in rctrls
            if ctrl_t.controlType == SimplePagedResultsControl.controlType
        ]
        if pctrls:
            if pctrls[0].cookie:
                # Copy cookie from response control to request control
                req_ctrl.cookie = pctrls[0].cookie

                msgid = self.search_ext(
                    settings.AD_SEARCH_DN,
                    ldap.SCOPE_SUBTREE,
                    search_flt,
                    attrlist=settings.AD_SEARCH_FIELDS.keys(),
                    serverctrls=(serverctrls or []) + [req_ctrl]
                )
            else:
                break
    return result_pages, all_results


class LDAPContextManager(object):

    """
    Context manager to handle LDAPObject lifetime. This could allow
    to restart operation by changing __enter__, or using memoization.
    """

    #FIXME: Exception not risen properly in case of fail

    def __init__(self, username, password, paged=False):
        """Init: initialize a LDAPObject, use correct options inject paged
        method if needed

        :param username/password credentials used to request LDAP isntance
            str that defines the url:port to LDAP server
        :param paged bool to set method for paged search
        """
        self.username = username
        self.password = password
        self.paged = paged
        
        self.ldap_url = LDAP_URL
        logger.info("Initialize LDAP connection to {0}".format(self.ldap_url))
        self.__ldap_connection = ldap.initialize(
            self.ldap_url, trace_level=LDAP_CONF_SETTINGS['TRACE_LEVEL'])
        _apply_ldap_options(self.__ldap_connection,
                            LDAP_CONF_SETTINGS['LDAP_SETTINGS'])

        if self.paged:
            # Adding the paged search
            logger.info("Patching LDAPObject instance with paged search")
            self.__ldap_connection.paged_search_ext_s = types.MethodType(
                _paged_search_ext_s, self.__ldap_connection)

    def __enter__(self):
        try:
            self._connect()
        except ConnectionError:
            self.__exit__(*sys.exc_info())
            import inspect
            sys.settrace(lambda *args, **keys: None)
            frame = inspect.currentframe(1)
            frame.f_trace = self.__trace
        return self

    def __trace(self, frame, event, arg):
        raise

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self._kill()
        except ConnectionError:
            # Let the context crashes if connection cannot be dealt with
            return False
        return True

    def connected(self):
        """Check if ldap_connection still exists."""
        return self.__ldap_connection is not None

    def _connect(self, username=None, password=None):
        """Handshake with LDAP.

        :param username: LDAP credentials
        :param password: LDAP credentials
        :return: Boolean if operation succeeded

        """
        # Get frame caller.
        # logger.debug('{0.f_code.co_filename}:{0.f_lineno}'.format(
        #     sys._getframe(1)))

        c_usern = username or self.username
        c_psswd = password or self.password

        if not c_psswd:
            logger.error("Blank password not allowed on login")
            raise ConnectionError("Blank password not allowed on login")

        try:
            logger.info("Connecting to Active Directory {0:s}".format(
                self.ldap_url))

            # auth_tokens = ldap.sasl.digest_md5(c_usern, c_psswd)
            # auth_tokens = ldap.sasl.sasl({
            #     ldap.sasl.CB_AUTHNAME: c_usern,
            #     ldap.sasl.CB_PASS: c_psswd,
            # }, 'DIGEST-MD5')
            # self.__ldap_connection.sasl_interactive_bind_s("", auth_tokens)
            self.__ldap_connection.simple_bind_s("MyDomain\\" + c_usern,
                                                 c_psswd)

        except ldap.INVALID_CREDENTIALS as e_ldap:
            logger.error("AD auth backend ldap errors - probably bad "
                         "credentials for {0:s}".format(c_usern))
            raise ConnectionError(e_ldap)

        except ldap.LDAPError as e_ldap:
            if type(e_ldap.message) == dict and 'desc' in e_ldap.message:
                logger.error("AD reset connection - it looks like invalid: "
                             "{0:s} ({1:s})".format(str(e_ldap.message['desc']),
                                                    get_exc_str()))
            else:
                logger.error("AD reset connection - it looks like invalid: "
                             "{0:s} ({1:s})".format(str(e_ldap), get_exc_str()))
            raise ConnectionError(e_ldap)
        except Exception as exx_cp:
            logger.error(exx_cp)
            raise ConnectionError(exx_cp.message)

        logger.info("Connected to Active Directory {0:s}".format(self.ldap_url))

    def _kill(self):
        """Disconnect from LDAP server."""
        try:
            if self.__ldap_connection:
                self.__ldap_connection.unbind_s()
                self.__ldap_connection = None
        except ldap.LDAPError as e_ldap:
            raise ConnectionError(e_ldap)

    def ldap_lookup(self, lookup_name=None):
        """Perform a lookup in the Active Directory

        :param lookup_name: name to lookup for in the Active Directory. If it
            contains a space, it will assume it is a full name and will make the
            proper LDAP query. Otherwise, will consider it as a username.

        :return: an array of fetched information from LDAP
        :exception ConnectionError
        """
        if not self.__ldap_connection:
            raise ConnectionError("Connection to the Active Directory {0:s} "
                                     "has been lost".format(self.ldap_url))

        # Here is the magic to either query with a username or with a full name:
        if lookup_name:
            if any(c in string.whitespace for c in lookup_name):
                # last_name = re.sub('ö', 'o', lookup_name.split()[0])
                # first_name = ' '.join(lookup_name.split()[1:])

                lkup_field = SEARCH_FLT.format('(cn={0})'.format(lookup_name))
            else:
                lkup_field = SEARCH_FLT.format('(sAMAccountName={0})'.format(lookup_name))
        else:
            lkup_field = SEARCH_FLT.format('(sn=*)')

        try:
            # LDAP searches (either paged or not)
            if not self.paged:
                res = self.__ldap_connection.search_ext_s(
                    settings.AD_SEARCH_DN,
                    ldap.SCOPE_SUBTREE,
                    lkup_field,
                    settings.AD_SEARCH_FIELDS.keys())
                # Assumes we get only one match from query (if username or full
                # name). It shall always be the case.
                #FIXME: What do you do with homonyms?
                if len(res[0]) > 2:
                    raise ConnectionError("LDAP query on users with {0:s} as"
                                             " argument returns more than one "
                                             "entry".format(lookup_name))
            else:
                _, res = \
                    self.__ldap_connection.paged_search_ext_s(
                        settings.AD_SEARCH_DN,
                        ldap.SCOPE_SUBTREE,
                        lkup_field,
                        attrlist=settings.AD_SEARCH_FIELDS.keys(),
                    )

        except ValueError:
            raise ConnectionError("{0} is missing from LDAP query".format(
                lookup_name))

        except ldap.LDAPError as exxcp:
            raise ConnectionError("Error in LDAP:\n{0}".format(exxcp))

        return res


def adaccount_validator(res_search):
    """Validate existence of keys in AD lookup.
    Return a list of boolean defining whether a value is in the search
    scheme.

    Kept in class definition for practical reasons (we will not validate the
    array retrieved from a LDAP query pretty much elsewhere).

    :param res_search: list(str) list of entries to lookup in LDAP
    :returns list of boolean values
    """
    #TODO: Add a hash map for what was the error for an invalid user, so
    # we can log this.
    #TODO: Use AD account validator from module
    return [prop for prop, required in
            settings.AD_SEARCH_FIELDS.iteritems() if required and
            prop not in res_search], \
           [prop for prop, required in
            settings.AD_SEARCH_FIELDS.iteritems() if not required and
            prop not in res_search]
