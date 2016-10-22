#!/usr/bin/env python3


class PeermeCmd():
    ''' Base class for all sub commands to inherit from '''

    def __init__(self, main_opts):
        ''' Store Global main arguments etc. '''
        self.opts = main_opts
