#!/usr/bin/env python3

'''
    Class to take care of peerme config
'''

import configparser
import logging


class PeermeConfig():

    def __init__(self, conf_file):
        self.conf_file = conf_file
        self.config = configparser.ConfigParser()
        self.config.read(conf_file)
        if not self.config.sections():
            self._default_load()
            return
        logging.info('Loaded {} config file'.format(conf_file))

    def _default_load(self):
        ''' Return a default config '''
        logging.warning('{} not found - Using default config'.format(
            self.conf_file
        ))
        self.conf_file = 'default'
        self.config['peerme'] = {
            'my_asn': 32934,
        }

    def __repr__(self):
        output = ''
        for section in self.config.sections():
            output += '{}\n'.format(section)
            for kv_pair in self.config.items(section):
                output += '  {}\n'.format(kv_pair)
        return output
