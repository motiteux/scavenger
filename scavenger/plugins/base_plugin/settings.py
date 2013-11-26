# -*- coding: utf-8 -*-

__author__ = 'marco'

import weakref
import json
import yaml
import collections


class BaseSettings(object):

    _SettingsPool = weakref.WeakValueDictionary()

    class _SettingsDict(object):

        """Class to handle a user-defined mapping to a dict and get parameter
        lookup for members, and all submembers.
        """

        def __init__(self, **entries):
            self.__dict__.update(entries)

        def update(self, entries):
            """Update keys in self members

            :param entries: keys
            """
            self.__dict__.update(entries)

        def __getitem__(self, name):
            """Retrieves a the dict entry with name, or greps all subdict with
            name and retrieve a dict with all entries. If none found, returns
            None"""

            try:
                return object.__getattribute__(self, name)
            except AttributeError:
                def nest(c_dict):
                    for key, value in c_dict.iteritems():
                        if isinstance(value, collections.Mapping):
                            for inner_key, inner_value in nest(value):
                                yield inner_key, inner_value
                        else:
                            yield key, value

                for item in nest(self.__dict__):
                    if name in item:
                        return item[1]
                else:
                    raise NotImplementedError("Attribute {0} does not exist in "
                                          "settings. Check your configuration "
                                          "file".format(name))

        def __getattribute__(*args):
            """Direct lookup on dict key, else gives a dict, always"""
            try:
                return object.__getattribute__(*args)
            except AttributeError:
                return {}

        def __iter__(self):
            for attr in self.__dict__:
                yield attr

        def __repr__(self):
            """Everything is a dict"""
            return '{\n%s\n}' % str(
                '\n'.join('\t%s : %s,' % (k, json.dumps(v,
                                                        sort_keys=True,
                                                        indent=8))
                          for (k, v) in self.__dict__.iteritems()))

    def __new__(cls, name, **kwargs):
        """Settings(name)

        Create a new settings object, or return an existing one from
        _SettingsPool
        """
        obj = BaseSettings._SettingsPool.get(name, None)

        if not obj:
            obj = object.__new__(cls)
            BaseSettings._SettingsPool[name] = obj

        return obj

    def __init__(self, name, **kwargs):
        super(BaseSettings, self).__init__(name, **kwargs)
        self.name = name
        self.settings = BaseSettings._SettingsDict()

    def __getattribute__(*args):
        """Go in settings attribute if could not find in base attributes"""
        try:
            return object.__getattribute__(*args)
        except AttributeError:
            return object.__getattribute__(args[0], 'settings')[args[1]]

    def _check(self):
        """Check if the settings is properly set up.

            "abstract method"
        """
        raise NotImplementedError

    def __unicode__(self):
        return u'{0}:\n{1}'.format(self.__class__.__name__, self.to_json())

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):     # must be unambiguous
        return repr(unicode(self))

    def to_json(self):
        return json.dumps(self,
                          default=lambda o: o.__dict__,
                          sort_keys=True,
                          indent=4)

    def to_yaml(self):
        return yaml.safe_dump(json.loads(self.to_json()),
                              default_flow_style=False,
                              encoding='utf-8')