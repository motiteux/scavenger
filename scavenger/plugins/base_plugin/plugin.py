#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Created on Nov 15, 2012

"""
Module doc
"""

__author__ = 'marco'

import os
import logging
import importlib
import imp


logger = logging.getLogger(__name__)


class PluginRegistry(type):
    plugins = []

    def __init__(cls, name, bases, attrs):
        if name != 'BaseFactory':
            PluginRegistry.plugins.append(cls)

        super(PluginRegistry, cls).__init__(name, bases, attrs)


class BasePlugin(object):

    """Base class for all factories. Allow plugin-like dynamic load, through its
    metaclass
    """

    __metaclass__ = PluginRegistry

    class BaseSettingsFactory(object):
        pass


def discover_plugins_directory(*dirs):
    """Discover the plugin classes contained in Python files, given a list of
        directory names to scan.
    """
    dirs = list(dirs)
    for directory in dirs:
        for filename in os.listdir(directory):
            modname, ext = os.path.splitext(filename)
            if ext == '.py':
                file_name, path, descr = imp.find_module(modname, [directory])
                if file:
                    try:
                        _ = imp.load_module(modname, file, path, descr)
                    except Exception as e:
                        logger.warning("could not load plugin module '%s': %s",
                                       modname, e.message)


def discover_plugins_packages(*modules_path):
    """Discover the plugin classes contained in the sys.path"""
    for module_name in modules_path:
        try:
            importlib.import_module(module_name)
        except ImportError as e:
            logger.warning("could not load plugin module '%s': %s",
                            module_name, e.message)