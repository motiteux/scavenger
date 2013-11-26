# -*- coding: utf-8 -*-

__author__ = 'marco'

import os

#from ..base_plugin.plugin import
from ..base_plugin.settings import BaseSettings


class SystemSettings(BaseSettings):
    def __init__(self, *argv, **kwargs):
        verbosity = kwargs.pop('verbosity', None)
        super(SystemSettings, self).__init__(*argv, **kwargs)

        self.settings.update({
            'logging': {
                'log_path': os.path.expanduser('~/.prometheus'),
                'verbosity': verbosity or 'INFO',
            },
        })

        self.file_settings = os.path.join(os.path.expanduser('~/.prometheus'),
                                          'prometheus.conf')
        self.serialize()

    def serialize(self):
        try:
            os.mkdir(os.path.dirname(self.file_settings))
        except OSError:
            pass
        with open(self.file_settings, 'w') as f_cfg:
            f_cfg.write(self.to_yaml())

    #class Factory(BaseFactory):
    #    def __call__(self, *args, **kwargs):
    #        return SystemSettings('system', *args, **kwargs)


system_settings = SystemSettings.Factory()()