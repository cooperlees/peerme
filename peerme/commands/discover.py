#!/usr/bin/env python3

'''
    Class to take care of discovering potential peers
'''

#import asyncio
import click
import logging

from .cli_common import PeermeCmd


class DiscoverCli():

    @click.command()
    @click.option(
        '-a',
        '--asn',
        help='ASN to discover common IXs.'
    )

    @click.pass_obj
    def discover(cli_opts, asn):
        ''' All Discovered potential peerings '''
        DiscoverPeers(cli_opts).run(asn)


class DiscoverPeers(PeermeCmd):

    # TODO: Delete
    async def dbTest(self):
        sql_data = await self.opts.db.execute_query()
        print("GOT '{}' from DB".format(sql_data))

    def run(self, asn):
        click.echo("Time to get some peers discovered - Debug = {}".format(
            self.opts.debug
        ))

        click.echo("Config {} = {}".format(self.opts.config.conf_file,
                                           self.opts.config))
        self.opts.db.MY_ASN = self.opts.config.config['peerme']['my_asn']
        if asn:
            peers_result = self.opts.loop.run_until_complete(
                self.opts.db.get_session_by_asn(asn))
        for peer in peers_result:
            print(peer)
