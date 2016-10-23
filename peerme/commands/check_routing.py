#!/usr/bin/env python3

'''
    Class to discover routing is as desired
'''

import click
import logging

from .cli_common import PeermeCmd


class CheckRoutingCli():

    @click.command()
    @click.option(
        '-d',
        '--dest-asn',
        type=int,
        help='Destination ASN for traffic',
    )
    @click.option(
        '-i',
        '--dest-ixp',
        help='Destination IXP for traffic',
    )
    @click.pass_obj
    def check_routing(cli_opts, dest_asn, dest_ixp):
        ''' Lets check the traffic paths are as desired '''
        CheckRouting(cli_opts).run(dest_asn, dest_ixp)


class CheckRouting(PeermeCmd):

    def run(self, dest_asn, dest_ixp):
        pass
