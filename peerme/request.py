#!/usr/bin/env python3

'''
    Class to talk to the Pinder API
'''

import click
import logging

from peerme import PeermeCmd


class RequestCli():

    @click.command()
    @click.pass_obj
    def pinder(cli_opts):
        ''' Request a right swipe or check the status of a peering request '''
	# TODO: Add request and status API calls
        RequestPeering(cli_opts).request()


class RequestPeering(PeermeCmd):

    def request(self):
        pass

    def status(self):
        pass
