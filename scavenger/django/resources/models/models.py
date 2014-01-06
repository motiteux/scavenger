#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Created on Nov 2, 2012

"""
Empty strings fields initialized at None
"""

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db.models import Q, AutoField
from django.db.models.query import EmptyQuerySet


@receiver(pre_save)
def update_nulls(sender, instance, **kwargs):
    for field in instance._meta.fields:
        if field.null and hasattr(instance, field.name) and \
                getattr(instance, field.name) == "":
            setattr(instance, field.name, None)

"""
Utils to query Fk(Group) with a limit_choice_to with QuerySet made out of a XOR.
No really portable like this. Need to use string.Template to improve lookup
fields genericity
"""
def query_xor(field_lookup, xor_set):
    """Get a XOR of the queries that match the group names in names_group.

    :param field_lookup: field lookup for the ORM
    :param xor_set: set of fields name to perform a XOR query
    """
    if not len(xor_set):
        return EmptyQuerySet()
    elif len(xor_set) == 1:
        lkup_query = {field_lookup: xor_set[0]}
        return Q(**lkup_query)

    lkup_query = {field_lookup: xor_set[0]}

    q_chain_or = Q(**lkup_query)
    q_chain_and = Q(**lkup_query)

    for name in xor_set[1:]:
        lkup_query = {field_lookup: name}
        query = Q(**lkup_query)
        q_chain_or |= query
        q_chain_and &= query

    return q_chain_or & ~q_chain_and


def copy_model_instance(obj):
    """Create a copy of a model instance.

    Works in model inheritance case where instance.pk = None is not good enough,
    since the subclass instance refers to the parent_link's primary key during
    save. M2M relationships are currently not handled, i.e. they are not copied.

    Reference: http://djangosnippets.org/snippets/1040/
    """
    initial = dict([(f.name, getattr(obj, f.name)) for f in obj._meta.fields
                    if not isinstance(f, AutoField) and
                    not f in obj._meta.parents.values()])
    return obj.__class__(**initial)