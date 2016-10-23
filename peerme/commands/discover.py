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
    @click.option(
        '--json',
        help='JSON output of peers',
        is_flag=True,
    )
    @click.pass_obj
    def discover(cli_opts, dest_asn, dest_ixp, json):
        ''' All Discovered potential peerings '''
        DiscoverPeers(cli_opts).run(dest_asn, dest_ixp, json)


class DiscoverPeers(PeermeCmd):

    def _json_output(self, peers):
        '''
            Dump some JSON for other potential tools to injest
        '''
        logging.error("To be developed. Come back soon or Pull Requests welcome")

    def _pretty_output(self, peers):
        base_format = '{:>6} {:>35} {:>15} {:>15} {:>15}'

        click.secho(base_format.format(
                'ASN',
                'v6 Addr',
                'v6 Pfx Limit',
                'v4 Addr',
                'v4 Pfx Limit',
            ),
            fg='green',
        )
        for peer in peers:
            click.secho('IX {}:'.format(peer.ix_desc), fg='red')
            click.echo(base_format.format(
                peer.asn,
                peer.peer_ipv6,
                peer.prefix_limit_v6,
                peer.peer_ipv4,
                peer.prefix_limit_v4,
            ))


    def run(self, dest_asn, dest_ixp, json=False):
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
        if json:
            self._json_output(peers_result)
        else:
            self._pretty_output(peers_result)
