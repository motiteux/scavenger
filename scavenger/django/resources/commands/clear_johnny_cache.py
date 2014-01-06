#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Created on 26/03/2013

"""Management command to clear Johnny Cache
From Gist https://gist.github.com/diox/1065196
"""

__all__ = [
    'Command'
]

import logging
from optparse import make_option

from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand, CommandError


logger = logging.getLogger('default.commands.clear_johnny_cache')


class Command(BaseCommand):
    help = ("Invalidates portions of the queryset cache based on the app names"
            " or models provided as arguments to the command. If no arguments "
            "are provided, nothing is done. To clear the entire queryset "
            "cache, use the --all_models option.")
    args = '[appname appname.ModelName ...]'
    option_list = BaseCommand.option_list + (
        make_option(
            '--all-models', dest='all_models', action='store_true',
            default=False, help='Invalidate the cache for all models.'
        ),
        make_option(
            '-e', '--exclude', dest='exclude', action='append', default=[],
            help='App to exclude (use multiple --exclude to exclude multiple '
                 'apps).'
        ),
    )

    def handle(self, *app_labels, **options):
        try:
            from django.db.models import get_app, get_apps, get_models, get_model
            from django.utils.datastructures import SortedDict
            from johnny.cache import invalidate
            from johnny.middleware import QueryCacheMiddleware

            # enable queryset cache
            q = QueryCacheMiddleware()

            all_models = options.get('all_models')
            exclude = options.get('exclude')

            excluded_apps = set(get_app(app_label) for app_label in exclude)
            app_list = None

            if all_models:
                if len(app_labels):
                    # FIXME: warn user that specifying apps on the command line when
                    # using -all-models options has no impact
                    pass
                app_list = SortedDict((app, None) for app in get_apps() if app not in excluded_apps)
            elif not len(app_labels) == 0:
                app_list = SortedDict()
                for label in app_labels:
                    try:
                        app_label, model_label = label.split('.')
                        try:
                            app = get_app(app_label)
                        except ImproperlyConfigured:
                            raise CommandError("Unknown application: %s" % app_label)

                        model = get_model(app_label, model_label)
                        if model is None:
                            raise CommandError("Unknown model: %s.%s" % (app_label, model_label))

                        if app in app_list.keys():
                            if app_list[app] and model not in app_list[app]:
                                app_list[app].append(model)
                        else:
                            app_list[app] = [model]
                    except ValueError:
                        # This is just an app - no model qualifier
                        app_label = label
                        try:
                            app = get_app(app_label)
                        except ImproperlyConfigured:
                            raise CommandError("Unknown application: %s" % app_label)
                        app_list[app] = None

            if app_list:
                # Generate a list of models to be invalidated, and call the Johnny
                # Cache invalidate command.
                full_model_list = []
                for app, model_list in app_list.items():
                    if model_list is None:
                        model_list = get_models(app)
                    if model_list:
                        full_model_list.extend(model_list)

                logger.info('Trying to clear cache for %d app(s), %d model(s) to invalidate' % (len(app_list), len(full_model_list)))

                for model in full_model_list:
                    logger.info('Invalidating cache for %s' % (model._meta.module_name))
                    invalidate(model)
                logger.info('Done invalidating')
            else:
                logger.info('No model to invalidate')
        except:
            logger.error("Could not clear Johnny Cache")