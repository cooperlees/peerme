#!/usr/bin/env python3

'''
    Class to take care of discovering potential peers
'''

import click
import logging

from .cli_common import PeermeCmd


class DiscoverCli():

    @click.command()
    @click.option(
        '-d',
        '--dest-asn',
        help='Destination ASN for traffic',
    )
    @click.option(
        '-i',
        '--dest-ixp',
        help='Destination IXP for traffic',
    )
    @click.pass_obj
    def discover(cli_opts, dest_asn, dest_ixp):
        ''' All Discovered potential peerings '''
        DiscoverPeers(cli_opts).run(dest_asn, dest_ixp)


class DiscoverPeers(PeermeCmd):

    def run(self, dest_asn, dest_ixp):
        #TODO: Support ixp
        self.opts.db.MY_ASN = self.opts.config.config['peerme']['my_asn']
        if dest_ixp and dest_asn:
            raise NotImplementedError('filtering on both dest_asn and dest_ixp not implemented')
        if dest_asn:
            peers_result = self.opts.loop.run_until_complete(
                self.opts.db.get_session_by_asn(dest_asn)
            )
        if dest_ixp:
            peers_result = self.opts.loop.run_until_complete(
                self.opts.db.get_session_by_ix(dest_ixp)
            )
        for peer in peers_result:
           click.echo(peer)
