#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Created on 08/04/2013

"""Active Directory Authentification Backend for UserProfile.

Mapping between ActiveDirectory attributes and member of UserProfile class is
defined in the settings variable AD_SEARCH_FIELDS.keys().

"""

__all__ = [
    'LDAPUser',
    'ActiveDirectoryBackend',
]

import datetime
import string
import re
import logging
import chardet

from django.conf import settings
from django.contrib.auth.models import User, Group
from django.contrib.auth.backends import ModelBackend
from django.core.cache import cache
from django.utils.timezone import utc
from django.utils.encoding import smart_unicode

from project.utils.cache import fix_key

from ..models import UserProfile
import userprofile.utils

import ldap_connector

class MyError(Exception):
    pass

class ConnectionError(Exception):
    pass


logger = logging.getLogger('userprofile.auth.backend')


class _MappingLDAP(object):

    """Class to handle a user-defined mapping to a dict and get parameter lookup
    for members.
    """
    #TODO: Need to look at ldap_ctx.py for a new approach: syncing with middle
    # class/model

    def __init__(self, **entries):
        self.__dict__.update(entries)

    def update(self, **entries):
        """Update keys in self members

        :param entries: keys
        """
        self.__dict__.update(entries)

    def __getattribute__(*args):
        """Specific need for a getattribute: some information may be missing in
        LDAP. If missing, return a list with an empty string. It would be like
        using defaultdict(list[0], ['']) but with member variables.

        **Notes:
        --------
            All entries from AD search are returned, and thus in MappingLDAP, as
            lists of strings/unicode
        """
        try:
            return object.__getattribute__(*args)
        except AttributeError:
            return ['']

    def __repr__(self):
        return '{%s}' % str('\n '.join('%s : %s,' % (k, repr(v))
                                       for (k, v) in self.__dict__.iteritems()))


class LDAPUser(object):

    """LDAP User manager

    Class used to gather and map LDAP/ActiveDirectory users to Django Users.

    """

    #TODO: May need to follow http://goo.gl/bomAa for synchronization between
    # profiles and LDAP accounts, instead of the cron jobs...

    def __init__(self, ldap_connection=None):
        """init method

        :param ldap_connection: LDAPContextManager instance, used for the
        handshake. This one was responsible to ensure a proper credential to
        present to Active Directory server
        """
        self.lookup_name = None
        self.username = None
        self.ldap_connection = ldap_connection

        self.is_active = True
        self.member_of = set()

        self.ad_data = _MappingLDAP()

        self.profile = None

    def teamleader_lkup(self, name):
        """Search in the ActiveDirectory for a member with name :param name.
        Name is either a username or a full name

        Will trigger a recursive lookup up to the top of the LDAP. Does not
        prevent an infinite loop if the Active Directory has a malformed tree
        structure.

        Each Lookup is cached if successful and retrieved on the next lookup
        from someone that is under the same team-leader.

        :param name: string specifying the lookup
        """
        logger.info("Retrieving information for teamleader {0:s}".format(
            name))
        if name is None:
            logger.error("LDAP info field (for supervisor) is missing")
            return None
        elif not any(c in string.whitespace for c in name):
            logger.error("LDAP info field (for supervisor) is malformed "
                         "(not as first name + last name)")
            return None
        elif name == self.username:
            logger.error("LDAP info field (for supervisor) is equal to current "
                         "username (he cannot be his/her own supervisor")
            return None

        # We cache the different team-leaders for a day. Most of them will
        # actually be fetched several times. So there is not a real need to
        # update them most often.
        name_key = fix_key(name)
        team_lead_pk = cache.get(name_key)

        #FIXME: Currently, LDAP connector does not allow reconnect
        if team_lead_pk is None and self.ldap_connection.connected():
            teamad_lookup = LDAPUser(self.ldap_connection)
            teamad_lookup.lookup_name = name

            team_lead = teamad_lookup.generate_user()
            if team_lead is not None:
                cache.set(name_key, team_lead.pk, 3600 * 24 * 31)

                logger.info("Retrieved information of team-leader {0:s} "
                            "for user {1:s}".format(name, self.lookup_name))
            else:
                logger.warning("No supervisor for user {0:s}".format(
                    self.lookup_name))
        else:
            try:
                team_lead = User.objects.get(pk=team_lead_pk)
            except User.DoesNotExist:
                logger.warning("Could not retrieve TL {0} from Django "
                               "db".format(name))
                team_lead = None

        return team_lead

    def update_information(self, ldap_result):
        """Update information from LDAP.

        :param ldap_result:
        """
        #TODO: Get a real account validator that raises something in case some
        # important information is missing
        logger.info("Validating retrieved information from ActiveDirectory")
        missing_reqs, missing_opts = ldap_connector.adaccount_validator(
            ldap_result)

        if missing_reqs:
            msg_miss = string.Template("Missing required data in "
                                       "ActiveDirectory for $user: $info ")
            data_miss = {'user': self.lookup_name,
                         'info': missing_reqs}
            logger.error(msg_miss.safe_substitute(data_miss))
            return False

        if missing_opts:
            msg_miss = string.Template("Missing optional data in "
                                       "ActiveDirectory for $user: $info ")
            data_miss = {'user': self.lookup_name,
                         'info': missing_opts}

            logger.warning(msg_miss.safe_substitute(data_miss))

        # We update our MappingLDAP data structure
        self.ad_data.update(**ldap_result)

        logger.debug("Data fetched from LDAP for {0}: {1}".format(
            self.lookup_name,
            self.ad_data))

        self.username = self.ad_data.sAMAccountName[0]

    def get_userdata(self):
        """Validate and return information from LDAP server.

        Separated from direct update from LDAP

        :returns Boolean if success fetched success
        :raise ConnectionError if LDAP error (no data or LDAP connection
                    problem.
        """
        if not self.ldap_connection.connected():
            logger.error("Connection to the Active Directory {0:s} has been "
                         "lost".format(self.ldap_connection.ldap_url))
            return False

        else:
            try:
                logger.info("Looking up in ActiveDirectory %s for user %s" % (
                    self.ldap_connection.ldap_url,
                    self.lookup_name)
                )
                result = self.ldap_connection.ldap_lookup(
                    lookup_name=self.lookup_name
                )
            except KeyError:
                raise ConnectionError("AD auth ldap backend error by "
                                         "searching {0}. No result.".format(
                                         settings.AD_SEARCH_DN))

            except ConnectionError:
                raise

            self.update_information(result[0][1])

    def create_or_update_userprofile(self,
                                     user,
                                     update=True,
                                     tree_update=False):
        """Create the user profile or update it

        :param user: Django User instance to create profile upon
        :param update: Boolean to flag the update of the UserProfile
        :param tree_update: Boolean to used to activate the signal post_save
            when UserProfile is saved.

        :return: a User instance
        :exception ConnectionError if management Groups were not added during
            setup
        """
        #TODO: Use last_visited and first_visit attributes to set update to
        # True if > 1 week (for example)
        if not update:
            return user

        group_exist = True
        try:
            user.first_name = self.ad_data.givenName[0]
            user.last_name = self.ad_data.sn[0][:27] + \
                (self.ad_data.sn[0][27:] and '...')
            user.email = self.ad_data.mail[0]
            user.is_active = self.is_active
            user.set_unusable_password()

            # Assigning group memberships
            user_groups = user.groups.all()

            for group in self.member_of:
                try:
                    t_group = Group.objects.get(name=group)
                    if t_group not in user_groups:
                        t_group.user_set.add(user)
                except Group.DoesNotExist:
                    # The exception raised here can be caught by calling
                    # codes to display proper information
                    logger.critical("The group %s has to be created in Django "
                                    "DB first" % group)
                    raise
        except Group.DoesNotExist:
            # Does propagate exception up to the trace: ModelBackend should
            # return None if auth fails
            group_exist = False
        else:
            logger.warning("ReBooK user data overriden for %s from "
                           "ActiveDirectory" % self.lookup_name)

        # save signal will create profile instance
        user.save()

        logger.info("Updating user profile info for %s." % self.lookup_name)
        self.profile = user.profile

        try:
            self.profile.last_name_prof = self.ad_data.sn[0]
            self.profile.job_title = self.ad_data.title[0]
            self.profile.telephone = self.ad_data.mobile[0]
            self.profile.team = self.ad_data.division[0]
            self.profile.department = self.ad_data.department[0]
            self.profile.city = self.ad_data.l[0]

            if self.ad_data.info[0] is not '' and \
                    self.ad_data.info[0] not in [
                        "{0} {1}".format(self.profile.last_name_prof,
                                         user.first_name),
                        "{0} {1}".format(user.first_name,
                                         self.profile.last_name_prof),
                        "{0}".format(self.lookup_name)]:
                try:
                    self.profile.team_leader = self.teamleader_lkup(
                        self.ad_data.info[0])
                except Exception as err:
                    logger.error("Could not retrieve TL {0} for user "
                                 "{1}".format(self.ad_data.info[0],
                                              self.lookup_name))
                    logger.error(err)
                    self.profile.team_leader = None
            else:
                self.profile.team_leader = None


            logger.info("Information updated in user profile for {0:s}".format(
                self.lookup_name))

            self.profile.save(tree_update=tree_update)

        except(AttributeError, IndexError) as exx_cp:
            logger.warning("Missing information for {0:s}.\n{1}".format(
                self.lookup_name, exx_cp))

        except Exception as err:
            raise MyError(err)

        return user

    def generate_user(self, tree_update=False, sync=True):
        """Retrieve or create a user, generate its profile if non-existent, and
        update them with inforamtion from Active Directory

        :param sync:
        :param tree_update:
        :return: User instance
        """

        if not self.ldap_connection.connected():
            logger.error("Connection to the Active Directory {0:s} has been "
                         "lost".format(self.ldap_connection.ldap_url))
            return None

        user = None

        try:
            user = User.objects.get(username=self.lookup_name)
        except User.DoesNotExist:
            try:
                if any(c in string.whitespace for c in self.lookup_name) and \
                        len(self.lookup_name.split()) > 2:
                    user = User.objects.get(
                        last_name=self.lookup_name.split()[0],
                        first_name=self.lookup_name.split()[1:])
            except User.DoesNotExist:
                logger.warning("User {0} did not exist in the Django DB".format(
                    self.lookup_name))

        try:
            self.get_userdata()

            created = False
            if not user:
                user, created = User.objects.get_or_create(
                    username=self.username,
                    defaults={
                        'is_staff': False,
                        'is_superuser': False}
                )

            if created:
                logger.info("User {0} did not existed in Django DB. Creating "
                            "it.".format(self.lookup_name))
            else:
                logger.info("User {0} already existed in Django DB. Updating "
                            "it.".format(self.lookup_name))

        except ConnectionError as exx_cp:
            logger.error("There was an error during the retrieval of data for "
                         "user {0}".format(self.lookup_name))
            logger.error(exx_cp)
            raise MyError(exx_cp)

        except Exception as err:
            logger.error("There was an error during the retrieval of data for "
                         "user {0}".format(self.lookup_name))
            logger.error(err.message)
            raise MyError(err.message)

        return user

    def __repr__(self):
        args = ['%s=%s' % (k, repr(v)) for (k, v) in vars(self).items()]
        return "{0:s}({1:s})".format(self.__class__.__name__,
                                     ", ".join(args))

    def __str__(self):
        return "{0:s}(<{1:s}>, connected={2:s}, , " \
               "has_data={3:s}, member_of={4:s})".format(
               self.__class__.__name__,
               self.lookup_name,
               self.ldap_connection.connected(),
               self.member_of)


class ActiveDirectoryBackend(ModelBackend):

    """Backend for connecting to Active Directory using LDAP."""

    def authenticate(self, username=None, password=None):
        """Overriding authenticate method for user/password to connect on the AD

        :param username: Credentials
        :param password: Credentials

        :return: User
        :raise ConnectionError if error in authentication
        """
        logger.info("Active Directory authentication for {0:s} at {1}".format(
            username, settings.AD_DNS_NAME))

        user = None

        c_password = ''
        if isinstance(password, str):
            enc_pass = chardet.detect(password)['encoding']
            c_password = smart_unicode(password,
                                       encoding=enc_pass).encode('utf-8')
        elif isinstance(password, unicode):
            c_password = password

        with ldap_connector.LDAPContextManager(username, c_password) \
                as ldap_conn:
            logger.info("User {0} could connect to ActiveDirectory".format(
                username))
            try:
                ad_lookup = LDAPUser(ldap_conn)
                ad_lookup.lookup_name = username

                user = ad_lookup.generate_user()

                logger.info("User {0:s} mapped".format(username))

            except MyError as err:
                # This exception could be re-raised for login views to catch and
                # deal with specifically
                logger.error(err.message)
                return None

        return user
